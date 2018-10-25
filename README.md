# paper.io.sessdsa
地空数算课2018期末作业：纸带圈地

【北京大学地空学院数据结构与算法课程实习作业2018】

【陈斌 gischen(at)pku.edu.cn】

课程网站：[【数据结构与算法Python版】](http://gis4g.pku.edu.cn/course/pythonds)

Collection of the reports can be found at the following site:

Link: https://pan.baidu.com/s/1JgX5pLu0-nEyU3dfxCk-nw

Password: 8hcp


## 比赛参数公告
### __建议先用棋盘大小102*101（k=51,h=101)，每局2000个回合，每局时限30秒__

上述参数在热身赛之后可能会根据赛情调整。

## 文件说明
- README.md：本文件
- LICENSE：授权文件GPL 3.0
- UPDATE.py：更新工具
* match_core.py：游戏执行逻辑（配套代码分析报告）
* match_interface.py：游戏逻辑接口
- sessdsa2018-paper.io.pdf：实习作业说明PPT
- paper_io_20180522.pdf：说明文档
- AI_Template.py：AI编写模板（配套说明pdf文件）
- [AI]：一些示例AI
* visualize.py：自定义比赛与记录回放工具
* glory_of_mankind.py：人机对战工具
- [_outdated]：过时的代码

## 修改历史
_注：以下成分缺少语句主语均为“技术组”_

### 20180610
- 陈斌上传了现场竞赛日程安排agenda.md；

### 20180608
- lineChartAbsoluteFields.py ：读入 zlog 可绘制各回合的双方领地绝对数值
- lineChartDisBands.py ：读入 zlog 可绘制各回合的双方纸卷与对方纸带距离
- lineChartDisScrolls.py ：读入 zlog 可绘制各回合的双方纸卷距离
- lineChartFieldRatio.py ：读入 zlog 可绘制各回合的双方领地相对大小

### 20180606
- 创建小组赛分组抽选代码

### 20180605
- 陈斌上传了实习作业报告模版
- 上传一对一连续20局执行使用的档案'knockout20.py'
- 更新文档
- 可视化比赛程序大修，增加直播比赛功能

### 20180604
- 创建多进程循环赛工具

### 20180603
- 取消基于线程的超时终止功能
- 更新完整的AI_Template

### 20180602
- 可视化工具与人机对战工具布局改为横向，增加文字输入框双击全选功能，实时显示各当前帧的双方领地大小
- 优化比赛记录存储方式
    - 由pkl文件改为压缩二进制文件，后缀名为zlog
- 将未跟进接口变化的代码移至“过时”目录内
- 增加用于循环赛与记分板实时更新的代码
- 上传新的 paper.io.sessdsa 文档

### 20180601
- 参数接口更改
    - 参数内容更改
        - stat现包括场地大小与比赛记录
        - storage改为多局比赛间不重置的私有存储
        - 原场地信息stat现为stat\['now'\]
        - 原场地大小storage\['size'\]现为stat\['size'\]
        - 原比赛记录storage\['log'\]现为stat\['log'\]
    - AI函数接口更改
        - load与summary函数增加比赛信息stat接收，详见AI_Template.pdf
- match_core.py中移除match_with_log函数
- 陈天翔创建游戏逻辑接口代码match_interface.py，增加多局对决功能
    - 多局比赛起始、结束函数接口暂定为init与summaryall

### 20180531
- 陈天翔创建人机对战工具

### 20180530
- 陈天翔为比赛可视化工具增加进度条功能

### 20180529
- 陈天翔优化内核log记录方式，并在load函数读入的存储中放置初始场景

### 20180527
- 陈天翔为内核增加对summary函数支持
- 陈天翔为内核增加match.DEBUG_TRACEBACK接口，便于调试

### 20180524
- 陈天翔将自定义比赛工具改为canvas显示，并增加了记录回放功能
- 陈天翔为内核增加帧读取接口
- 陈天翔创建了本地更新工具

### 20180523
- 陈天翔为内核代码增加超时终止功能

### 20180522
- 张赖和创建了期末大作业总说明文档
- 陈天翔创建了比赛工具
- 陈天翔为内核代码增加了load函数接口，并修改了相关代码读取玩家AI的逻辑

### 20180521
- 陈天翔上传了控制台复盘代码，修改了执行逻辑使之支持可变回合数/思考时间，并上传了示例随机游走AI
- 陈天翔更改复盘文件格式（由shelve对象改为pkl格式）与输出路径（保存至log文件夹）
- 张赖和创建了循环赛代码，并上传了另外4个示例AI
- 陈天翔创建了AI模板与配套的说明文件

### 20180520
- 陈天翔上传了游戏执行逻辑

### 20180519
- 陈斌创建了实习作业说明PPT。

### 20180518
- 陈斌创建代码仓库和README.md文件。