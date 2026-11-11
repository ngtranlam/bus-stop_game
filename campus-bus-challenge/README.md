# Campus Bus Challenge (캠퍼스 셔틀 정차 챌린지)

Game 2D viết bằng Python + Pygame cho dự án cuối kỳ môn Tư duy máy tính (컴퓨팅 사고).
Xe buýt trường chạy ngang màn hình. Nhấn **Space** đúng lúc để dừng xe sao cho
**tâm xe** (vạch đỏ dưới thân xe) trùng với **tâm trạm** (vạch đen giữa vùng màu).
Đồ họa pixel-art được vẽ hoàn toàn bằng code, không dùng file ảnh hay âm thanh.

## Cài đặt và chạy

Yêu cầu: Python 3.10 trở lên. Đã chạy thử với Python 3.13.5 và pygame 2.6.1.

**macOS / Linux**

```bash
cd campus-bus-challenge
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python "20231855- 팜 응옥 아잉- FinalProject.py"
```

**Windows (PowerShell)**

```powershell
cd campus-bus-challenge
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python "20231855- 팜 응옥 아잉- FinalProject.py"
```

File game đã được đặt tên theo quy định nộp bài: `20231855- 팜 응옥 아잉- FinalProject.py`.

## Điều khiển

| Phím | Tác dụng |
|---|---|
| Enter | Bắt đầu ván ở màn hình tiêu đề |
| Space | Dừng xe (chỉ có tác dụng khi xe đang chạy) |
| P | Tạm dừng / tiếp tục |
| R | Chơi lại ở màn Game Over |
| Esc hoặc nút đóng cửa sổ | Thoát game |

## Luật chơi

- **Chấm điểm** theo `distance = |tâm xe - tâm trạm|`:

  | Khoảng cách | Hạng | Điểm | Mạng |
  |---|---|---:|---|
  | ≤ 12 px | PERFECT | 100 + thưởng combo | giữ nguyên |
  | ≤ 32 px | GOOD | 60 | giữ nguyên |
  | ≤ 65 px | OK | 30 | giữ nguyên |
  | > 65 px | MISS | 0 | −1 |

- Nhấn quá sớm cũng tính là MISS. Nếu không nhấn, khi tâm xe vượt quá `tâm trạm + 65` thì game tự tính MISS.
- **Combo** là số PERFECT liên tiếp. Thưởng = `min(combo − 1, 5) × 20`, nên điểm PERFECT lần lượt là 100, 120, 140 … và tối đa 200. GOOD, OK hoặc MISS sẽ đưa combo về 0. Combo vẫn được giữ khi lên màn.
- **Màn chơi:** mỗi màn có 3 trạm, MISS cũng tính là một trạm. Bắt đầu với 3 mạng và không có cách hồi mạng.
- **Tốc độ:** `min(260 × 1.15^(level − 1), 520)` px/giây, tức là 260 → 299 → 344 → 395 → 455 → 520 (tối đa).
- Màn 1 là buổi sáng, màn 2 buổi chiều, màn 3 buổi tối. Từ màn 4 trở đi lặp lại chu kỳ này.

## Cấu trúc code

Toàn bộ nằm trong một file `20231855- 팜 응옥 아잉- FinalProject.py`, chia thành 4 phần:

1. **Logic thuần** (không vẽ, test được): `calculate_speed`, `calculate_grade`, `calculate_points`,
   `new_game_state`, `start_stop`, `new_run`, `resolve_stop`, `press_space`, `finish_result`,
   `toggle_pause`, `move_bus`.
2. **5 hàm chính:** `init()`, `handle_input()`, `update_game()`, `render()`, `run_game()`.
3. **Tài nguyên đồ họa:** sprite được viết dưới dạng danh sách chuỗi ký tự (mỗi ký tự là một ô 4×4 px),
   rồi `build_sprite()` chuyển chúng thành hình.
4. **Hàm vẽ:** các hàm `draw_*` chỉ đọc state và không thay đổi luật chơi.

Trạng thái game được lưu trong một `dict`. Các hàm trả về dict mới (`{**state, ...}`) thay vì sửa dict cũ.

Các trạng thái của game: `TITLE → PLAYING → RESULT → (LEVEL_TRANSITION) → PLAYING … → GAME_OVER`.
Trạng thái `PAUSED` ghi nhớ `previous_state` để khi tiếp tục thì quay lại đúng chỗ.

## Kiểm thử

```bash
python -m unittest discover -s tests -v
```

`tests/test_rules.py` gồm 27 test cho các nhóm sau:

- ngưỡng chấm điểm (0, 12, 12.01, 32, 32.01, 65, 65.01; lệch trái và lệch phải);
- chuỗi combo 100 → 200 và các trường hợp làm mất combo;
- công thức tốc độ, trần 520, level rất lớn không gây tràn số;
- mỗi lượt chỉ được chấm một lần (bấm Space nhiều lần, tự MISS);
- chuyển màn, Game Over, chơi lại;
- Pause ở PLAYING / RESULT / LEVEL_TRANSITION;
- Esc và đóng cửa sổ ở mọi trạng thái.

## Hạn chế đã biết

- Không có âm thanh.
- Không lưu điểm cao nhất xuống đĩa.
- Chữ trên giao diện dùng font mặc định của Pygame (render không khử răng cưa), không phải font pixel thật.
- Ở tốc độ tối đa (520 px/s, 60 FPS) mỗi frame xe đi khoảng 8.7 px, nên vùng PERFECT 24 px chỉ kéo dài khoảng 2–3 frame. Game vẫn chơi được nhưng rất khó.
- Kiểm thử tự động chỉ kiểm tra logic và vòng lặp bằng sự kiện giả lập. Cảm giác điều khiển cần người chơi thử trực tiếp.
