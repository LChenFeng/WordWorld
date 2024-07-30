# 文字世界

一个2D侧视开放像素世界游戏（开发中）

### 系统要求

| 名            | 版本                       |
|--------------|--------------------------|
| python       | 3.10+（`match`改`if`可3.8+） |
| pygame       | 2.6.0                    |
| numpy        | 2.0.0                    |
| pywin32      | 306                      |
| perlin-noise | 1.12                     |

## 介绍

### [视频](https://pd.qq.com/s/vn04ibrh)

#### 世界大小
1920x128

#### 支持6763个方块（汉字）和177个符号、字母、数字（功能慢慢更新）

#### 已知bug
- UI可能错位（目前适配1980x1080<sup>v0.4.1+</sup>和1360x768分辨率)
- 人物运动偶尔穿模

### 矿物
目前有9种自然生成的矿物
- 煤
- 蜡
- 铁
- 金
- 铜
- 钛
- 钨
- 钚
- 铀

## 合成表

#### "木" "板" "棍" "台" "门" "梯"与Minecraft无异

#### 桌 ：提供4x4合成

<table>   
  <tr>  
    <th colspan="3">输入</th>  
    <th>输出</th>  
  </tr>
    <tr>
      <td>钢</td>  
      <td>钢</td> 
      <td>钢</td>
      <td rowspan="2">桌</td>
    </tr>  
    <tr> 
      <td>钢</td>  
      <td> </td>  
      <td>钢</td>
  </tr> 
</table> 

#### 烛：照明

<table>   
  <tr>  
    <th>输入</th>  
    <th>输出</th>  
  </tr>
    <tr>
      <td>蜡</td>
      <td rowspan="2">烛x4</td> 
    </tr>  
    <tr> 
      <td>蜡</td>
    </tr>
</table> 

#### 灯：照明

<table>   
  <tr>  
    <th>输入</th>  
    <th>输出</th>  
  </tr>
    <tr>
      <td>铁</td>
      <td rowspan="3">灯x2</td> 
    </tr>  
    <tr> 
      <td>蜡</td>
    </tr>
    <tr>
      <td>铁</td>
    </tr>
</table> 

#### 字：打破后随机获得一个汉字

<table>   
  <tr>  
    <th>输入</th>  
    <th>输出</th>  
  </tr>
    <tr>
      <td>符x2</td>
      <td>字</td>
    </tr>
</table> 

#### 符：打破后随机获得一个符号/字母/数字

<table>   
  <tr>  
    <th>输入</th>  
    <th>输出</th>  
  </tr>
    <tr>
      <td>字</td>
      <td>符x2</td>
    </tr>
</table> 

#### （部分物质和合成表为新增，老版本没有）

## 获取方块

由于目前没有创造模式物品栏，大部分方块需要通过代码获取

#### 步骤

打开`main.py`，找到`load_player()`函数，
`player.knap.add(...)`即为设定初始背包物品的语句  
语法：`player.knap.add(Items(方块id, [数量]))`  
方块id在`Data/json/blocks/`下的2个文件中，数量默认为1
