# 期末课程设计 · 四位加法器

[← 信息与电子工程导论](../../index.md) · [全部实验报告](../index.md)

使用晶体管实现半加器和全加器，并组合为四位串行进位加法器，包含逻辑推导、Multisim 仿真和实物验证。

报告仅供参考，请独立完成课程设计。

- [打开 / 下载课程设计报告（PDF）](report.pdf)
- [查看逻辑推导公式独立阅读页](formulas.md)

<details class="report-pdf" data-pdf="report.pdf">
<summary>展开课程设计 PDF 预览</summary>
</details>

## 公式阅读版

第 5–7 页的公式已按照原稿修复。下面另附可复制的公式，便于在线阅读。

## 最低位：半加器

$$
S_0=\overline{A_0}B_0+A_0\overline{B_0}=A_0\oplus B_0
$$

$$
C_1=A_0\cdot B_0
$$

## 高位：两级半加器

$$
S^{\prime}=A_i\oplus B_i
$$

$$
C^{\prime}=A_i\cdot B_i
$$

$$
S_i=S^{\prime}\oplus C_i=(A_i\oplus B_i)\oplus C_i
$$

$$
C^{\prime\prime}=S^{\prime}\cdot C_i=(A_i\oplus B_i)\cdot C_i
$$

## 进位输出逻辑合成

$$
C_{i+1}=C^{\prime}+C^{\prime\prime}
$$

$$
C_{i+1}=A_i\cdot B_i+(A_i\oplus B_i)\cdot C_i
$$

## 四位加法器整体逻辑方程组

$$
S_0=A_0\oplus B_0
$$

$$
C_1=A_0\cdot B_0
$$

$$
S_1=A_1\oplus B_1\oplus C_1
$$

$$
C_2=A_1\cdot B_1+(A_1\oplus B_1)\cdot C_1
$$

$$
S_2=A_2\oplus B_2\oplus C_2
$$

$$
C_3=A_2\cdot B_2+(A_2\oplus B_2)\cdot C_2
$$

$$
S_3=A_3\oplus B_3\oplus C_3
$$

$$
C_4=A_3\cdot B_3+(A_3\oplus B_3)\cdot C_3
$$

其中 $i=1,2,3$，$C_4$ 为溢出位；输入为 $A_3A_2A_1A_0$ 和 $B_3B_2B_1B_0$。
