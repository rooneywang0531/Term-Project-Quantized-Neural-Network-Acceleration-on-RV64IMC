# Xqmac v0.3：完整模型所需指令

RV64 only。所有指令為 32-bit R4：rs3[31:27]、funct2[26:25]、rs2[24:20]、rs1[19:15]、funct3[14:12]、rd[11:7]、opcode[6:0]。

| 指令 | opcode | funct3 | funct2 | match | mask |
|---|---:|---:|---:|---:|---:|
| qmac4.ss | 0x0b | 0 | 0 | 0x0000000b | 0x0600707f |
| qmac4.us | 0x0b | 1 | 0 | 0x0000100b | 0x0600707f |
| qrequant.dr | 0x2b | 0 | 0 | 0x0000002b | 0x0600707f |
| qrequant.sr | 0x2b | 1 | 0 | 0x0000102b | 0x0600707f |

保留既有 MAC／DR 編碼；新增 SR 後，custom-1 funct3=1 已合法，reserved-funct3 測試改用 2。
每次執行先擷取三個舊來源再寫 rd；來源可彼此 alias，rd 可 alias 任意來源。
x0 來源讀 0，寫入丟棄；非法 operand 即使 rd=x0 仍須 trap。
來源 upper32 全忽略，結果為 INT32 的 RV64 sign extension。
RV32、保留 funct2／funct3、非法 RQ operand 均觸發 illegal instruction，不能 writeback。

## Packed MAC

`qmac4.ss/us rd, rs1, rs2, rs3`：

- rs1：四個低位元組 activation；ss 模式 signed8，us 模式 unsigned8。
- rs2：四個 signed8 weights。
- rs3：低 32 bits accumulator。
- lane i 對應 bits 8i+7:8i。
- 將四個乘積與 accumulator 相加，modulo 2^32，再 sign-extend 到 RV64。
- 無 rounding、飽和、zero-point 或 clamp。

## Double-rounding RQ

`qrequant.dr rd, rs1, rs2, rs3`：x=signed32(rs1)，m=unsigned32(rs2)，r=unsigned32(rs3)。
合法 m=0..2^31-1、r=0..31；不將 r 截成低五位。

```text
p = x*m
nudge = 2^30 if p>=0 else 1-2^30
h = trunc_toward_zero((p+nudge)/2^31)
if r==0: y=h
else:
    mask=2^r-1
    remainder=h mod 2^r             # nonnegative remainder
    threshold=floor(mask/2)+(h<0)
    y=floor(h/2^r)+(remainder>threshold)
rd=sign_extend_64(y)
```

精確取代目前 Conv／ADD helper；原 helper 的非正 shift=s，傳入 r=-s。
兩次 rounding 不合併。合法域內 y 可用 INT32 表示，不需飽和。

## Single-rounding RQ

`qrequant.sr rd, rs1, rs2, rs3`：x=signed32(rs1)，m=unsigned32(rs2)，r=unsigned32(rs3)。
合法 m=0..2^31-1、r=31..62；不將 r 截成低六位。

```text
y=floor((x*m+2^(r-1))/2^r)
rd=sign_extend_64(y)
```

單次 nearest rounding，正負 half tie 均朝 +infinity，精確對應原 FC 的 arithmetic-shift 表達式。
原 FC 傳入 r=31-shift，模型實際為 38..40。合法域內結果落在 INT32。
這條 SR 不等同 DR，不能互換。未定義負 multiplier、r<31 的 left-scaling／飽和行為。

所有 RQ 的 zero-point 加法、activation clamp 和 INT8 store 均留在 C。

## 微架構後續工作

三來源 R4 在雙讀埠 RF 可分兩階段擷取 operand；需保留同一條指令的來源值，處理 RAW forwarding、
stall、flush／kill、alias 與 precise exception，且每條指令只能 retire 一次。
MAC／乘法／rounding 可以多週期或 pipeline；Spike callback 不表示一個 cycle。
cycle、CPI、時脈、面積與記憶體 stall 須後續 RTL／綜合量測。
