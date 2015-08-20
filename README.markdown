# Sublime Text 3 plugin: quick Open  
you're not always want open everthing in sublime;  
eg you just want open folder in file explorer or .psd in photoshop;  
QuickOpen can open file or directory with system default way  

## 常用功能  
-| 在explorer中打开文件夹  
-| 用默认的软件打开相关文件  
-> 比如 .psd 用 photoshop 打开  
-> 你可以自己在quickOpen.sublime-settings设置需要文件类型  
-> "openOutList": [".psd", ".lnk", ".zip", "..."]  

-| 在 show_quick_panel 选择文件自动补全  


## 常见问题  
-| 文件夹文件过多, 查找需要时间  
-> 你可以设置 maxSearchTime  
-> 如果是3s 就设置为 "maxSearchTime": 3000  
---&&---  
-| 同时超过时间还没有搜索完, 会弹出一个提示框你可以选择去掉  
-> "hideMessageDialog": true  
