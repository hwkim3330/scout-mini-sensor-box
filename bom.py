import geom as g
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
F = "Arial"; th = Side(style="thin", color="999999"); B = Border(left=th, right=th, top=th, bottom=th)
HF = PatternFill("solid", fgColor="1F4E79"); IN = PatternFill("solid", fgColor="FFF2CC")
wb = Workbook()
def sheet(ws, title, cols, rows, widths, note=None, price_cols=None):
    ws.title = title
    r0 = 1
    if note:
        ws.cell(1, 1, note).font = Font(name=F, size=9, italic=True, color="555555"); r0 = 3
    for j, c in enumerate(cols, 1):
        x = ws.cell(r0, j, c); x.font = Font(name=F, bold=True, color="FFFFFF", size=10); x.fill = HF; x.alignment = Alignment(vertical="center", wrap_text=True); x.border = B
    for i, row in enumerate(rows, r0 + 1):
        for j, v in enumerate(row, 1):
            x = ws.cell(i, j, v); x.font = Font(name=F, size=9.5); x.border = B; x.alignment = Alignment(vertical="top", wrap_text=True)
    for j, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = ws.cell(r0 + 1, 1)
    return r0
fab = [
 ["P01", "BOTTOM PLATE", "AL5052-H32", 3.0, 1, "Laser", "CLSS-M4-2 ×10 (트레이 4 + 전장판 6), CSK ×12", "P01_BOTTOM_PLATE.dxf", 671],
 ["P02", "WALL HALF – FRONT (C1/C2/C3)", "AL5052-H32", 2.0, 1, "Laser + Bend (2×60°, 2×90°)", "CLSS-M3-1 ×18, CLSS-M4-1 ×6", "P02_WALL_HALF_FRONT.dxf", 394],
 ["P03", "WALL HALF – REAR (C4/C5/C6)", "AL5052-H32", 2.0, 1, "Laser + Bend (2×60°, 2×90°)", "CLSS-M3-1 ×22, CLSS-M4-1 ×6", "P03_WALL_HALF_REAR.dxf", 371],
 ["P04", "TOP COVER", "AL5052-H32", 2.0, 1, "Laser", "— (Ø5.5 ×4). 도장 시 P11 접촉부 140×140 MASK", "P04_TOP_COVER.dxf", 411],
 ["P05", "OS1 MOUNT PLATE", "AL6061-T6", 5.0, 1, "Laser / CNC + Tap", "M5 TAP ×4 (B). OS1 접촉면 Ø100 + 하면 BARE MASK. OS1 홀 HOLD", "P05_OS1_PLATE.dxf", 261],
 ["P06", "CAMERA ADAPTER PLATE", "AL5052-H32", 2.0, 8, "Laser", "— (lens/holder HOLD, KETI)", "P06_CAMERA_PLATE.dxf", 17],
 ["P07", "REAR SERVICE PANEL", "AL5052-H32", 2.0, 1, "Laser", "—", "P07_SERVICE_PANEL.dxf", 34],
 ["P08", "AGX TRAY", "AL5052-H32", 2.0, 1, "Laser + Bend (4×90°)", "CSK ×4. 70×70 = ADAPTER/CABLE CLEARANCE (HOLD 5, 그대로 가공)", "P08_AGX_TRAY.dxf", 68],
 ["P09", "WALL SPLICE BRACKET", "AL5052-H32", 2.0, 2, "Laser + Bend (1×60°)", "—", "P09_SPLICE_BRACKET.dxf", 23],
 ["P10", "ELECTRICAL PLATE (탈착식)", "AL5052-H32", 2.0, 1, "Laser", "— (Ø3.4 그리드, PEM 없음)", "P10_ELEC_PLATE.dxf", 156],
 ["P11", "OS1 RISER FRAME", "AL6061-T6", 25.0, 1, "CNC + Tap (M5 ×8, 10DP)", "무처리 BARE (도장/아노다이징 금지), 평면도 0.05", "P11_OS1_RISER.dxf (외형 참고) + 도면 SHEET 8", 532],
]
PEM_TOTAL = 62
ws = wb.active
cols = ["품번", "품명", "재질", "두께 t(mm)", "수량", "공정", "PEM / 후가공", "DXF", "단품 질량(g, 계산)", "단가 A 무처리(원)", "단가 B 분체도장(원)", "금액 A", "금액 B"]
r0 = sheet(ws, "FAB_PARTS", cols, [r + [None, None] for r in fab], [7, 30, 13, 9, 7, 26, 34, 26, 12, 14, 14, 14, 14],
           note="노란 칸 = 제작사 견적 입력. 질량 = 3D 모델 체적 × 2.68 g/cm³. 금액 = 수량 × 단가 (자동).")
n = len(fab)
for i in range(r0 + 1, r0 + 1 + n):
    for c in (10, 11): ws.cell(i, c).fill = IN
    ws.cell(i, 12, f"=E{i}*J{i}").font = Font(name=F, size=9.5); ws.cell(i, 13, f"=E{i}*K{i}").font = Font(name=F, size=9.5)
    for c in (10, 11, 12, 13): ws.cell(i, c).number_format = "#,##0"; ws.cell(i, c).border = B
t = r0 + 1 + n
ws.cell(t, 2, "합계").font = Font(name=F, bold=True)
ws.cell(t, 9, f"=SUMPRODUCT(E{r0+1}:E{t-1},I{r0+1}:I{t-1})").font = Font(name=F, bold=True)
ws.cell(t, 12, f"=SUM(L{r0+1}:L{t-1})").font = Font(name=F, bold=True); ws.cell(t, 13, f"=SUM(M{r0+1}:M{t-1})").font = Font(name=F, bold=True)
ws.cell(t, 7, "PEM 총계 = 10 + 24 + 28 = %d ea (REV8 114)" % PEM_TOTAL).font = Font(name=F, size=9, italic=True)
for c in (9, 12, 13): ws.cell(t, c).number_format = "#,##0"
ws.cell(t + 2, 1, "표면처리 [A] 무처리 / [B] 흑색 분체도장 — 열접촉면 BARE 마스킹: P05 상면 Ø100 + 하면, P11 전체 무처리, P04 상면 140×140. 공차·검사: 도면 SHEET 1, 10.").font = Font(name=F, size=9, italic=True)

pur = [
 # cat, item, spec, qty_need, spare, where, note
 ["FASTENER", "M3×8 버튼헤드 (ISO 7380)", "SUS304 A2", 40, 10, "커버 12, 카메라 24, 서비스 4", ""],
 ["FASTENER", "M4×8 접시머리 육각홈 (ISO 10642)", "SUS304 A2", 16, 4, "하판 12, 트레이 4", ""],
 ["FASTENER", "M5×12 육각홈 (ISO 4762) + 평와셔 M5", "SUS304 A2", 4, 2, "P05 → P11 탭 A", ""],
 ["FASTENER", "M5×10 육각홈 (ISO 4762) + 평와셔 M5", "SUS304 A2", 4, 2, "P04 하면 → P11 탭 B", "직결 옵션 시 → P05 탭 B"],
 ["FASTENER", "M8×16 육각홈 (ISO 4762) + 평와셔 M8 (ISO 7089)", "SUS304 A2", 4, 2, "레일 이어 슬롯", "규격·길이 = 레일 확인 후 (HOLD 2)"],
 ["FASTENER", "SCOUT 레일 T-너트 M8", "레일 규격 따름", 4, 2, "레일", "HOLD 2 — 레일 피치·홈 폭 확인"],
 ["FASTENER", "M3×10 육각홈 + M3 나일록 너트 + 와셔", "SUS304 A2", 6, 4, "D-size 커넥터 ×3", ""],
 ["FASTENER", "M4 육각 스탠드오프 M-F 25 (수 6)", "Al 또는 황동", 4, 0, "AGX 트레이", "30/35는 B0473 fit check 결과 (HOLD 5)"],
 ["FASTENER", "M4 육각 스탠드오프 M-F 30 / 35", "Al 또는 황동", 8, 0, "AGX 트레이 높이 조정", "옵션"],
 ["FASTENER", "블라인드 리벳 Ø3.2 돔헤드, 그립 3.0~4.8", "Al/Al", 12, 8, "벽 스플라이스", "제작사 조립 시 제작사 지급 가능"],
 ["FASTENER", "M4 육각 스탠드오프 M-F 10 (수 6)", "Al 또는 황동", 6, 2, "P10 전장판", ""],
 ["FASTENER", "M4×8 버튼헤드 (ISO 7380)", "SUS304 A2", 6, 2, "P10 → 스탠드오프", ""],
 ["FASTENER", "M3 볼트 + 나일론 스페이서 + 나일록 너트 키트", "Nylon/SUS", 1, 0, "P10 부품 (DC/DC, CAN Pal, WAGO, 5G)", "M3 6~20mm"],
 ["FASTENER", "M3×8 육각홈 (OS1 장착)", "SUS / 12.9", 4, 2, "OS1 → P05", "길이: OS1 나사 깊이 확인 (HOLD 3)"],
 ["FASTENER", "M2×6 + 너트/스페이서 (카메라 모듈)", "SUS", 24, 8, "B0473 ×6 → P06", "HOLD 4"],
 ["CONNECTOR", "케이블 글랜드 M16×1.5 + 로크너트 (클램프 4.5~10)", "니켈황동 IP68 (예: Lapp SKINTOP MS-M 16)", 1, 1, "P07 — SCOUT 확장 케이블", "케이블 외경 확인"],
 ["CONNECTOR", "분할형 케이블 글랜드 M32 (커넥터 통과형)", "IP54 이상", 1, 0, "P04 — OS1 케이블", "OS1 케이블 외경/커넥터 확인"],
 ["CONNECTOR", "etherCON 피드스루 D-size (Neutrik NE8FDP 또는 동등)", "Cat6", 1, 0, "P07 D1", ""],
 ["CONNECTOR", "USB 3.0 A↔A 피드스루 D-size (Neutrik NAUSB3 또는 동등)", "", 1, 0, "P07 D2", ""],
 ["CONNECTOR", "D-size 블랭크 플레이트 / 12V DC 잭 D-size", "", 1, 0, "P07 D3", "선택"],
 ["CONNECTOR", "SMA 벌크헤드(F) – U.FL/IPEX 피그테일 15cm", "50Ω", 4, 0, "P07 SMA", "5G 모뎀 확정 후 (HOLD 7)"],
 ["ELECTRICAL", "SCOUT 확장 케이블: 동봉 4핀 항공 플러그 + 4C 케이블 (AWG18 ×2 + 트위스트 CAN) 1 m", "납땜 제작", 1, 0, "H1", "위고 제작 요청 중 / 불가 시 KETI 납땜"],
 ["CABLE", "Arducam 15-22pin FPC 60cm", "Arducam 정품", 2, 1, "먼 2면 카메라", "기본 30cm ×6 동봉, 60cm 별도"],
 ["ELECTRICAL", "ATO 인라인 퓨즈홀더 AWG16~18 + ATO 5A 퓨즈", "", 1, 2, "24V 인입", "퓨즈 예비 2"],
 ["ELECTRICAL", "WAGO 221-413 레버 커넥터", "3P", 4, 2, "24V/GND 분배", ""],
 ["ELECTRICAL", "전선 AWG18 적/흑", "UL1015", 3, 0, "전원 (m)", "단위 m"],
 ["ELECTRICAL", "트위스트 페어 AWG24", "", 1, 0, "CAN (m)", "단위 m"],
 ["ELECTRICAL", "DC 배럴 플러그 5.5/2.5 피그테일", "센터 +", 1, 1, "AGX J41", ""],
 ["ELECTRICAL", "DC/DC 24→12V (기존품 사양 미달 시에만 대체)", "입력 19~36V, 12V 연속 ≥8A (예: Mean Well SD-100B-12)", 0, 0, "P10 장착", "HOLD 6 — 기존품 실측 후 수량 결정"],
 ["ELECTRICAL", "듀폰 점퍼 F-F 20cm", "", 4, 4, "CAN Pal ↔ J30", ""],
 ["MISC", "EPDM 폼 테이프 10×3 (점착)", "", 2, 0, "커버·하판 가스켓 (m)", "옵션 방진"],
 ["MISC", "EPDM 패드 1t 110×110", "", 1, 0, "AGX 트레이", ""],
 ["MISC", "벨크로 스트랩 25mm × 300", "", 2, 1, "AGX 고정", ""],
 ["MISC", "케이블 타이 + 타이 마운트 (M3)", "", 20, 0, "하네스", ""],
 ["MISC", "나사 고착제 중강도 (Loctite 243 등)", "", 1, 0, "", ""],
 ["OPTION", "OPT-2 벤트 방진 메쉬 (SUS 100mesh, 내측 접착)", "", 4, 0, "C1/C3/C4/C6 벤트", "분진 환경 시"],
]
ws2 = wb.create_sheet()
cols = ["구분", "품목", "규격/재질", "필요 수량", "예비", "주문 수량", "사용처", "비고", "단가(원)", "금액(원)", "구매처"]
r0 = sheet(ws2, "PURCHASED", cols, [[p[0], p[1], p[2], p[3], p[4], None, p[5], p[6], None, None, None] for p in pur],
           [12, 46, 30, 9, 7, 9, 26, 32, 11, 12, 16], note="노란 칸 = 입력. 주문 수량 = 필요 + 예비 (자동). 구매처 예: 미스미코리아 / 나사몰 / 디바이스마트 / 엘레파츠.")
for i in range(r0 + 1, r0 + 1 + len(pur)):
    ws2.cell(i, 6, f"=D{i}+E{i}").font = Font(name=F, size=9.5)
    ws2.cell(i, 10, f"=F{i}*I{i}").font = Font(name=F, size=9.5)
    for c in (9, 11): ws2.cell(i, c).fill = IN
    for c in (6, 9, 10, 11): ws2.cell(i, c).border = B
    for c in (9, 10): ws2.cell(i, c).number_format = "#,##0"
t = r0 + 1 + len(pur)
ws2.cell(t, 2, "합계").font = Font(name=F, bold=True); ws2.cell(t, 10, f"=SUM(J{r0+1}:J{t-1})").font = Font(name=F, bold=True); ws2.cell(t, 10).number_format = "#,##0"

hold = [
 [1, "SCOUT 4핀 항공 플러그 모델", "동봉 플러그에 케이블 납땜 → M16 글랜드 통과", "없음", "위고/KETI", ""],
 [2, "레일 피치 230 / 홈 폭 / T-너트", "매뉴얼 5.2 도면·실측·위고 회신으로 확정", "P01 슬롯 가공 전 필수", "KETI", ""],
 [3, "OS1 4×M3 + Ø2 핀 패턴", "보유 OS1 실측/템플릿 → P05 후가공", "P05 블랭크 납품", "KETI", ""],
 [4, "B0473 홀더 홀/렌즈 위치", "납품 키트 실측 → P06 후가공", "P06 블랭크 납품", "KETI", ""],
 [5, "B0473 어댑터 FIT CHECK", "AGX 카메라 커넥터(J509) 결합 후 하부 돌출/케이블 경로 확인 → P08 70×70 유지·축소, 스탠드오프 25/30/35", "없음 (P08 그대로 가공)", "KETI", ""],
 [6, "기존 24→12V DC/DC 실물 사양", "12V 연속 ≥8A, 피크 ≥10A, 효율 ≥90% 확인 전 전원 확정 금지", "없음 (P10 장착)", "KETI", ""],
 [7, "5G 모뎀/안테나", "모델 확정 → P10 장착, SMA 4홀 기가공", "없음", "KETI", ""],
]
ws3 = wb.create_sheet()
sheet(ws3, "HOLD", ["#", "HOLD 항목", "해제 방법", "판금 발주 영향", "담당", "완료일"], hold, [5, 34, 50, 24, 10, 12])
rfq = ["[견적 요청] KETI 모빌리티플랫폼연구센터 — SCOUT MINI 센서/컴퓨트 박스 판금 (REV 9, 최종)",
       "",
       "1. 품목: P01~P11 (FAB_PARTS 시트), 1세트 (P06 8개, P09 2개). 옵션 수량 3세트 / 5세트 단가 병기 요청.",
       "2. 재질: AL5052-H32 2.0T / 3.0T, AL6061-T6 5.0T (P05), AL6061-T6 25T (P11, CNC).",
       "3. 공정: 레이저 → PEM 압입 (PennEngineering CLSS 또는 동등, %d개) → 절곡 → 벽 링 리벳 조립 (P02+P03+P09). P05/P11 탭, P11 CNC." % PEM_TOTAL,
       "4. 표면: [A] 무처리, [B] 흑색 분체도장 — 분리 견적. 열접촉면 BARE: P05 상면 Ø100·하면, P11 전체, P04 140×140.",
       "5. 첨부: 도면 PDF 10매, DXF 11종 (외형·홀 MASTER), STEP (조립/부품), 본 BOM.",
       "6. 요청: 견적서 (A/B), 납기, 제작사 BD 반영 재전개 DXF 사전 회신, 첫 절곡품(벽 1면) 치수 확인 후 본 가공.",
       "7. 검사: 도면 SHEET 9 출하검사 항목 (AF300±0.5, H125±0.3, 플랜지 19±0.3, PEM 전수, 가조립 체결).",
       "8. 제외: 체결류·커넥터·장치 (PURCHASED 시트, 별도 구매). 장치 종속 홀 (HOLD) 가공 제외.",
       "9. 문의: hwkim3@keti.re.kr"]
ws4 = wb.create_sheet("RFQ")
for i, l in enumerate(rfq, 1):
    c = ws4.cell(i, 1, l); c.font = Font(name=F, size=10, bold=(i == 1))
ws4.column_dimensions["A"].width = 130
wb.save("out/SBOX_REV9_BOM.xlsx"); print("saved")
