# 要不要把quickOpenHistory中和当前没有关系的上去掉
import sublime, sublime_plugin
import os, webbrowser
import re
import threading

SETTINGS_FILE = 'quickOpen.sublime-settings'
openOutList = sublime.load_settings(SETTINGS_FILE).get('openOutList')
maxSearchTime = sublime.load_settings(SETTINGS_FILE).get('maxSearchTime')
hideMessageDialog = sublime.load_settings(SETTINGS_FILE).get('hideMessageDialog')

class quickOpenCommand(sublime_plugin.TextCommand):
	# 超过一定时间直接禁用
	def run(self, edit=None, url=None):
		work = ThreadQuickOpen(self)
		work.start()

class completePath(sublime_plugin.TextCommand):
	def run(self, edit=None, url=None):
		file_name = self.view.file_name()
		if not file_name:
			return

		work = ThreadCompletePath(self)
		work.start()

class ThreadQuickOpen(threading.Thread):
	orignal = None
	def __init__(self, orignal):
		self.orignal = orignal
		self.killed = False
		sublime.set_timeout(lambda: kill(self), maxSearchTime)
		threading.Thread.__init__(self)
	def run(self):
		orignal = self.orignal
		files = []
		pathList = []
		quickOpenHistory = []

		project_data = orignal.view.window().project_data()
		if project_data and 'settings' in project_data:
			if 'quickOpen_history' in project_data["settings"]:
				quickOpenHistory = project_data["settings"]["quickOpen_history"]

		def on_done(selected):
			if selected == -1:
				return
			curItem = pathList[selected]

			for history_item in quickOpenHistory:
				if curItem == history_item:
					quickOpenHistory.remove(history_item)
			quickOpenHistory.insert(0, curItem)

			if project_data and 'settings' in project_data:
				project_data["settings"]["quickOpen_history"] = quickOpenHistory[:10]
				orignal.view.window().set_project_data(project_data)

			# file
			path = curItem
			if os.path.isfile(path):
				webbrowser.open_new_tab(path)
			else:
				orignal.view.window().run_command('open_dir', { "dir": path})

		# 获取project 所有文件夹, 和相关文件
		if not orignal.view.window().project_data():
			return;
		projectfolders = orignal.view.window().project_data().get('folders')
		if len(projectfolders) == 0:
			return
		for item in projectfolders:
			allpath = getFolderFiles(item.get('path'), orignal=self, type=None, filetypes = openOutList)
			if type(allpath) == list:
				files.extend(allpath)
		if type(files) == list:
			pathList.extend(files)

		# 打开历史
		historyList = []
		for history_item in quickOpenHistory:
			for index, pathListItem in enumerate(pathList):
				if pathListItem == history_item:
					historyList.append(pathListItem)
					pathList.remove(pathListItem)
					break
				if index == len(pathList) - 1:
					quickOpenHistory.remove(history_item)

		pathList = historyList + pathList

		TpathList = prettifyPath(pathList)
		orignal.view.window().show_quick_panel(TpathList, on_done)

class ThreadCompletePath(threading.Thread):
	orignal = None
	def __init__(self, orignal):
		self.orignal = orignal
		self.killed = False
		sublime.set_timeout(lambda: kill(self), maxSearchTime)
		threading.Thread.__init__(self)
	def run(self):
		pathList = []
		orignal = self.orignal
		dirname = os.path.dirname(orignal.view.file_name())

		def on_done(selected):
			if selected == -1:
				return
			curItem = pathList[selected]

			path = curItem
			if os.path.isfile(path):
				pathT = os.path.relpath(path, dirname).replace("\\","/")

				orignal.view.run_command('insert_snippet', {"contents": pathT})

		projectfolders = orignal.view.window().project_data().get('folders')
		for item in projectfolders:
			if item.get('path') not in dirname:
				continue
			allpath = getFolderFiles(item.get('path'),orignal = self,  type="file")
			if type(allpath) == list:
				pathList.extend(allpath)

		TpathList = prettifyPath(pathList)
		orignal.view.window().show_quick_panel(TpathList, on_done)


def getFolderFiles(path, orignal, type = None, filetypes = None):
	sublime.status_message('on finding what you want!')

	pathlist = []
	settings = sublime.active_window().active_view().settings()
	excludeFiles = r'|'.join([x[1:] +'$' for x in settings.get('file_exclude_patterns')]) or r'$.'
	excludefolders = r'|'.join([x for x in settings.get('folder_exclude_patterns')]) or r'$.'
	for root, dirs, files in os.walk(path):
		if orignal.killed:
			if not hideMessageDialog:
				sublime.message_dialog(path + ': has  too many files, can\'t completely lsit!!')
			else:
				sublime.log_commands(path + ': has  too many files, can\'t completely lsit!!')
			orignal.killed = False
			break

		if re.search(excludefolders, root):
			continue
		if type != "file":
			root = root.replace("\\","/")
			pathlist.append(root)
			if type == "folder":
				continue
		for file in files:
			file = os.path.join(root, file).replace("\\","/")
			if re.search(excludeFiles, file):
				continue
			if filetypes:
				fileName, fileExtension = os.path.splitext(file)
				if not fileExtension in filetypes:
					continue

			pathlist.append(file)

	sublime.status_message('finding end')
	return pathlist

def prettifyPath(pathList):
	panelShow = []
	projectfolders = sublime.active_window().project_data().get('folders')
	for path in pathList:
		if len(projectfolders) == 1:
			pfpath = projectfolders[0]['path']
		elif len(projectfolders) > 1:
			for pf in projectfolders:
				if pf['path'].replace("\\","/") in path:
					pfpath = pf['path']
					break
		relpath = os.path.relpath(path, pfpath)
		if relpath == '.':
			relpath = os.path.basename(pfpath)
		elif len(projectfolders) > 1:
			relpath = os.path.basename(pfpath) + '\\' + relpath
		if os.path.isfile(path):
			panelShow.append(["[⬇] » " + os.path.basename(path) + " "*50, relpath])
		elif os.path.isdir(path):
			panelShow.append(["[➹] » " + os.path.basename(path) + " "*50, relpath])
	return panelShow

def kill(orignal):
	if orignal.killed == True:
		return
	orignal.killed = True