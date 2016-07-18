# 简介

expr是为了将某些变动较大的业务脱离主业务系统而设计的表达式语法。

# 语法

expr支持25种表达式类型，它们的分别如下所示（按优先级排序）：

## 原子类型

- 整数：1,2,3
- 小数：1.23
- 逻辑数：true, false
- 空：nil
- 字符串："Hello world"
- 括号表达式：(1+2)

## 复合类型

- 数组引用：list[0]
- 对象引用：math.pi
- 函数调用：add(1, 2)

## 单目运算符

- 负数: -
- 非: !

## 算术运算符

- 乘: *
- 除: /
- 模: %

- 加: +
- 减: -

## 比较运算符

- 大于: >
- 大于等于: >=
- 小于: <
- 小于等于: <=

- 等于: ==
- 不等于: !=

## 逻辑运算符

- 与: &&

- 或: ||

- 判断: expr if expr else expr

# 样例

```
"equal" if (math.add(1, 2) + 3 == 6) == (math.add(3, 9) / 4 == 3) else "not equal"
```
