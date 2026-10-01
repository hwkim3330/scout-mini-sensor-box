import math, geom as g
from drawlib import *
from shapely.geometry import Polygon, box, Point, LineString
from shapely import affinity
TOTAL = 10

def face_to_world(face, tau, z):
    x, y = g.face_point(face, tau, 0); return (x, y, z)

def elev_features(v, view="rear"):
    """draw elevation of box. view rear: from -Y, sx = x ; side: from +X, sx = y"""
    def sx(p):
        return p[0] if view == "rear" else p[1]
    vis = [f for f in g.FACES if (g.nvec(f)[1] < -0.1 if view == "rear" else g.nvec(f)[0] > 0.1)]
    # bottom plate
    bp = g.bottom_plate()["outline"]; mn, mx = (bp.bounds[0], bp.bounds[2]) if view == "rear" else (bp.bounds[1], bp.bounds[3])
    v.poly(box(mn, 0, mx, g.T_BOT))
    # wall silhouette
    rc = g.SIDE
    if view == "rear": xs = [-rc, -rc / 2, rc / 2, rc]
    else: xs = [-g.AF / 2, 0, g.AF / 2]
    v.poly(box(xs[0], g.T_BOT, xs[-1], g.Z_WALL_TOP))
    for xx in xs[1:-1]: v.line((xx, g.T_BOT), (xx, g.Z_WALL_TOP), lw=LW_O * 0.7)
    cw = g.COVER_AF / 2 if view == "side" else g.COVER_AF / math.sqrt(3)
    v.poly(box(-cw, g.Z_WALL_TOP, cw, g.H_TOTAL))
    zr = g.H_TOTAL + g.RISER_T
    v.poly(box(-70, g.H_TOTAL, 70, zr), fill="#e4e4ea")
    v.poly(box(-54, g.H_TOTAL, 54, zr), lw=LW_C, color=GRAY, ls=(0, (3, 2)))
    v.text(58, g.H_TOTAL + g.RISER_T / 2, "P11", fs=4.2, va="center", ha="right")
    v.poly(box(-70, zr, 70, zr + g.T_OS1))
    v.poly(box(-43.5, zr + g.T_OS1, 43.5, zr + g.T_OS1 + 74.2), color=BLUE, ls=(0, (6, 2)), lw=LW_T)
    v.text(0, zr + 40, "OUSTER OS1\n(Ø87, H74.2 w/ cap)", fs=4.8, ha="center", va="center", color=BLUE)
    for f in vis:
        for kind, geo, label in g.face_features(f, 1):
            if kind in ("win", "vent"):
                pts = [face_to_world(f, x, z) for x, z in geo.exterior.coords]
                v.poly(LineString([(sx(p), p[2]) for p in pts]), lw=LW_T)
        cp = g.cam_plate()["outline"]
        pts = [face_to_world(f, x, z + g.CAM_Z) for x, z in cp.exterior.coords]
        v.poly(LineString([(sx(p), p[2]) for p in pts]), lw=LW_O * 0.8)
        if f == g.SERVICE_FACE:
            sp = g.svc_plate()
            pts = [face_to_world(f, x, z + g.SVC_Z) for x, z in sp["outline"].exterior.coords]
            v.poly(LineString([(sx(p), p[2]) for p in pts]), lw=LW_O * 0.8)
            for h in sp["holes"]:
                p = face_to_world(f, h["x"], h["y"] + g.SVC_Z); v.circle(sx(p), p[2], h["d"], lw=LW_T)
        c = face_to_world(f, 0, g.CAM_Z); v.cmark(sx(c), c[2], 2)
        v.tag(sx(c), c[2] - 34, f, fs=5)

def sheet_cover(pdf):
    sh = Sheet("SENSOR / COMPUTE ENCLOSURE — 제작 도면 세트 (RFQ RELEASE)", 1, TOTAL, part=dict(no="ASSY-SBOX-R9", name="DRAWING INDEX / GENERAL NOTES", mat="see part list", qty="1 set"))
    sh.image("out/iso_front.png", 14, 168, 120, 102)
    sh.image("out/iso_open.png", 138, 168, 108, 102)
    sh.text(16, 166, "그림 1. 조립 외관 (REV 9)          그림 2. 상판 분리 – 내부 AGX 트레이 / 서비스 패널", fs=5.2, color=GRAY)
    cols = [("품번", 16), ("품명", 34), ("재질 / 두께", 30), ("수량", 10), ("가공", 36), ("인서트 / 표면", 30)]
    rows = [
        ["P01", "BOTTOM PLATE", "AL5052-H32 3.0T", "1", "LASER", "CLSS-M4-2 ×10, CSK ×12"],
        ["P02", "WALL HALF – FRONT", "AL5052-H32 2.0T", "1", "LASER + BEND 4", "CLSS-M3-1 ×18, M4-1 ×6"],
        ["P03", "WALL HALF – REAR", "AL5052-H32 2.0T", "1", "LASER + BEND 4", "CLSS-M3-1 ×22, M4-1 ×6"],
        ["P04", "TOP COVER", "AL5052-H32 2.0T", "1", "LASER", "— (P11 접촉부 MASK)"],
        ["P05", "OS1 MOUNT PLATE", "AL6061-T6 5.0T", "1", "LASER/CNC + TAP", "!M5 TAP ×4, 접촉면 BARE"],
        ["P06", "CAMERA ADAPTER PLATE", "AL5052-H32 2.0T", "8", "LASER", "— (6 + 2 spare)"],
        ["P07", "REAR SERVICE PANEL", "AL5052-H32 2.0T", "1", "LASER", "—"],
        ["P08", "AGX TRAY", "AL5052-H32 2.0T", "1", "LASER + BEND 4", "CSK ×4"],
        ["P09", "WALL SPLICE BRACKET", "AL5052-H32 2.0T", "2", "LASER + BEND 1", "—"],
        ["P10", "ELECTRICAL PLATE (탈착)", "AL5052-H32 2.0T", "1", "LASER", "— (Ø3.4 GRID)"],
        ["P11", "OS1 RISER FRAME", "AL6061-T6 25T", "1", "CNC + TAP", "!M5 TAP ×8, 무처리 BARE"],
    ]
    y = sh.table(250, 270, cols, rows, fs=5.0, rh=4.2)
    sh.text(250, y - 3.5, "PEM 합계 62개 (REV8 114개). 구매품 전체 목록: SBOX_REV9_BOM.xlsx", fs=4.8, color=GRAY)
    idx = [("1", "INDEX / GENERAL NOTES / REVISION"), ("2", "GENERAL ASSEMBLY (치수·인터페이스)"), ("3", "P01 BOTTOM PLATE"),
           ("4", "P02 WALL HALF – FRONT (전개/성형)"), ("5", "P03 WALL HALF – REAR + SERVICE OPENING"), ("6", "P04 TOP COVER / P05 OS1 PLATE"),
           ("7", "P06 / P07 / P08 / P09 SMALL PARTS"), ("8", "P10 ELECTRICAL PLATE / P11 OS1 RISER + FOV"),
           ("9", "INTERNAL LAYOUT / WIRING / POWER BUDGET"), ("10", "HARNESS / HOLD / INSPECTION / RFQ")]
    sh.table(250, y - 7, [("SHEET", 14), ("CONTENTS", 142)], idx, fs=5.0, rh=4.0)
    notes = [
        "1. 단위 mm. 레이저 외형·홀 좌표는 DXF가 기준(MASTER), 성형 치수·공차·후가공은 본 도면이 기준.",
        "2. 일반공차 ISO 2768-m. 레이저 외형/홀 ±0.1, 절곡 성형치수 ±0.3, 절곡각 ±0.5°, 평면도 0.5/100.",
        "3. 절곡 내R 2.0 (2T). DXF 전개는 K=0.40 참고치 — 제작사 금형 BD로 재전개 허용 (성형 외곽·홀 위치 유지).",
        "4. PEM: PennEngineering CLSS(스테인리스) 또는 동등품, 절곡 전 압입. 총 62개.",
        "5. 버 제거, 외곽 C0.3~0.5. 케이블/벤트 슬롯 버 제거 철저(FPC·케이블 손상 방지).",
        "6. 표면: [A] 무처리 기본 견적 + [B] 흑색 분체도장 옵션 별도 견적 (PEM/탭 나사부 마스킹).",
        "!6a. 열접촉면 분체도장 금지 (BARE AL 마스킹): P05 상면 OS1 접촉부 Ø100 + P05 하면 전체,",
        "!     P11 전체 무처리, P04 상면 P11 접촉부 140×140.  — THERMAL CONTACT SURFACE KEEP BARE ALUMINUM",
        "7. P02+P03+P09 리벳 조립(벽 링) 및 P01/P04 가조립 체결 확인까지 제작사 범위.",
        "!8. 장치 실측 종속 홀(OS1 4×M3·핀, 카메라 홀더)은 발주 제외 — 블랭크 납품, KETI 후가공 (SHEET 10 HOLD).",
    ]
    sh.box(14, 92, 232, 70, "GENERAL NOTES / 일반 주기", notes, fs=5.1, lh=5.5)
    rev = [
        "REV 8 → REV 9 변경 (견적 최종판)",
        "a) P08 중앙 70×70: 'ADAPTER / CABLE CLEARANCE — HOLD UNTIL B0473 ADAPTER FIT CHECK'로 재정의.",
        "    REV8의 'J509 하부' 표기 삭제 (J509 = 캐리어보드 상면, 모듈 하부 영역 카메라 커넥터 — 어댑터 직결).",
        "!b) P01 M3 PEM 그리드 54개 삭제 → M4 PEM 6개 + 탈착식 전장판 P10 (Ø3.4 레이저 그리드). PEM 114 → 62.",
        "!c) OS1: P05 → P11 AL6061 25T 라이저 프레임 → P04. 하향 −22.5° 전 범위 확보 (가림 경계 −23.8°).",
        "    P04 M5 PEM 삭제 → 하면 M5 볼트. 라이저 제거 직결 옵션 유지 (P05 탭 B, 가림 경계 −15.4°).",
        "!d) P05 / P11 / P04 열접촉면 분체도장 금지 (BARE AL).",
        "e) 전원 HOLD 6 유지 (기존 DC/DC 연속 ≥8A 확인 전 확정 금지). CAN: J30 p29/p31, CAN Pal 3.3V 구동 확정.",
        "",
        "REV 8: 레일 슬롯 외부 이어(Y±132), 2분할 절곡 벽, HOLD 블랭크화, 서비스 패널 확정, 전원 예산",
        "REV 7: 개념 GA / 배선 / 하네스 (제작 불가)",
    ]
    sh.box(14, 17, 232, 72, "REVISION HISTORY", rev, fs=5.1, lh=5.4)
    scope = ["[제작사 범위] P01~P11 레이저·절곡·CNC·탭·PEM 압입·버 제거·각인",
             "  + 벽 링 리벳 조립(P02+P03+P09) + P01/P04 가조립 체결 확인",
             "  + 표면처리 옵션 [B] 견적 분리 (6a 마스킹 포함)",
             "[납품] 개별 포장, 벽 링은 조립 상태. 체결류(BOM 구매품)는 제외",
             "[제외] 장치 종속 홀(HOLD) 후가공, 전장/하네스, 장치 조립",
             "[제출 요청] 견적서(A/B 구분) · 납기 · 재전개 DXF(BD 반영)",
             "  · 첫 절곡품 치수 확인서(AF300, H125, 플랜지 19, 홀 피치)",
             "[검사] SHEET 10 INSPECTION 항목 기준"]
    sh.box(250, 50, 160, 56, "발주 범위 / SCOPE OF SUPPLY", scope, fs=5.1, lh=5.6)
    sh.save(pdf)

def sheet_ga(pdf):
    sh = Sheet("GENERAL ASSEMBLY — 외형 / 인터페이스 치수", 2, TOTAL, part=dict(no="ASSY-SBOX-R9", name="GENERAL ASSEMBLY", mat="—", qty="1", scale="1:3"))
    s = 1 / 3
    # TOP VIEW
    v = View(sh, 105, 204, s, "TOP VIEW  (FRONT = +Y = C2)   1:3", 105, 268)
    bp = g.bottom_plate()
    v.poly(bp["outline"], lw=LW_T)
    for sl in bp["slots"]: v.poly(sl["shape"], lw=LW_T)
    v.poly(g.round_convex(g.hex_poly(g.COVER_AF), 4.0))
    v.poly(g.rrect(0, 0, 140, 140, 10), lw=LW_T)
    v.circle(0, 0, 87, color=BLUE, lw=LW_T)
    for h in g.top_cover()["holes"]: v.circle(h["x"], h["y"], h["d"], lw=LW_T)
    for sx in (-1, 1):
        v.line((sx * g.RAIL_X, -175), (sx * g.RAIL_X, 175), lw=LW_T, color=GRAY, ls=(0, (8, 2, 1, 2)))
    v.text(g.RAIL_X - 2, -40, "SCOUT RAIL CL (350)", fs=4.2, color=GRAY, rotation=90, va="center", ha="right")
    for f, ang in g.FACES.items():
        n = g.nvec(f); p = (n[0] * 150, n[1] * 150); q = (n[0] * 175, n[1] * 175)
        v.ax.annotate("", xy=v.P(*q), xytext=v.P(*p), arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=0.6, mutation_scale=6))
        v.tag(n[0] * 188, n[1] * 188, f"{f} {ang}°", fs=4.6)
    v.dim((-g.RAIL_X, g.RAIL_Y), (g.RAIL_X, g.RAIL_Y), 14, "230 (RAIL PITCH)", orient="h")
    v.dim((g.RAIL_X, -g.RAIL_Y), (g.RAIL_X, g.RAIL_Y), -30, "264", orient="v")
    v.dim((-g.SIDE, 0), (g.SIDE, 0), -60, "346.4 ACROSS CORNERS (MOLD)", orient="h")
    v.dim((-g.SIDE / 2, -150), (-g.SIDE / 2, 150), 40, "300 AF", orient="v")
    v.leader((g.RAIL_X, -g.RAIL_Y), "RAIL SLOT 9×20 (4×)  M8 SHCS + WASHER → T-NUT", 22, -8, fs=4.6)
    v.leader((0, -100), "Ø32.5 OS1 CABLE (M32 SPLIT GLAND)", -60, -8, fs=4.6)
    v.leader((60, 60), "P05 140×140 + P11 RISER 25T", 62, 22, fs=4.6)
    # REAR ELEVATION
    e = View(sh, 105, 58, s, "VIEW A — REAR (from −Y)   1:3", 105, 40)
    elev_features(e, "rear")
    e.dim((-g.SIDE, 0), (-g.SIDE, g.H_TOTAL), 8, "130", orient="v")
    e.dim((g.SIDE, 0), (g.SIDE, g.T_BOT), -6, "3", orient="v")
    e.dim((g.SIDE, g.Z_WALL_TOP), (g.SIDE, g.H_TOTAL + g.RISER_T + g.T_OS1), -6, "32", orient="v")
    e.dim((-g.SIDE, 0), (-g.SIDE, g.CAM_Z), 16, "92 CAM CL", orient="v")
    e.dim((-g.SIDE, 0), (-g.SIDE, g.H_TOTAL + g.RISER_T + g.T_OS1 + 74.2), 24, "234.2 (OS1 TOP)", orient="v")
    e.dim((-g.SIDE / 2, 0), (-g.SIDE / 2, g.SVC_Z), 6, "35", orient="v")
    # SIDE VIEW
    sv = View(sh, 232, 58, s, "VIEW B — RIGHT (from +X)   1:3", 200, 40)
    elev_features(sv, "side")
    sv.dim((-150, 0), (150, 0), -12, "300", orient="h")
    sv.dim((-g.RAIL_Y, 0), (g.RAIL_Y, 0), -4, "264 SLOT CL", orient="h")
    sh.image("out/iso_rear.png", 292, 160, 114, 110)
    lines = ["인터페이스 / INTERFACE",
             "• 로봇: SCOUT MINI 상부 레일 2열, 피치 230 — 이어 슬롯 4×(9×20), 슬롯 CL Y=±132",
             "  레일 T-너트/볼트 규격 HOLD → 기본 M8 (슬롯 9 = M8 클리어런스)",
             "• 카메라: 각 면 중앙, CL 높이 Z92, 60° 간격 6면 (C1~C6)",
             "• LiDAR: OS1 하면 = Z160 (P04 + P11 라이저 25 + P05 5)",
             "  빔 원점 Z196.2, 하향 −22.5° 전 범위 확보 (가림 −23.8°)",
             "  직결 옵션(P11 제거): OS1 하면 Z135, 가림 −15.4°",
             "• 서비스: C5(후면) 하단 패널 156×52, 케이블 하네스 출입",
             "• 냉각: C1/C3/C4/C6 하단 벤트 4×36 슬롯 ×9",
             "• 질량(예상): 판금·라이저 3.0 kg + 장치 ≈ 5.5 kg",
             "체결 요약 (SUS A2)",
             "• 커버: M3×8 BH ×12 → 벽 상부 플랜지 PEM",
             "• 하판: M4×8 FH ×12 (하면 접시) → 벽 하부 플랜지 PEM",
             "• OS1: P05→P11 M5×12 ×4 (A), P04 하면→P11 M5×10 ×4 (B)",
             "• 카메라 플레이트 M3×8 BH ×24 / 서비스 패널 M3×8 BH ×4",
             "• 벽 스플라이스: Al 블라인드 리벳 Ø3.2 ×12",
             "• 커버·하판 접합면: EPDM 폼 가스켓 10×3 (옵션 방진)"]
    sh.box(292, 48, 114, 108, None, lines, fs=4.8, lh=6.0)
    sh.save(pdf)
