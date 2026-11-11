# Nhật ký phát triển (dùng cho mục 8 và mục 9 của báo cáo)

## Nhật ký sử dụng AI

| Bước | Prompt / yêu cầu (người dùng) | Kết quả AI | Kiểm tra / chỉnh sửa |
|---|---|---|---|
| 1 | Prompt (1) trong file hướng dẫn: đề xuất 3 game 2D làm bằng Pygame | 3 ý tưởng, chọn "캠퍼스 셔틀 정차 챌린지" | Luật gốc là 5 lượt cộng điểm, sau đó được mở rộng |
| 2 | "Đọc và phân tích đề bài này" (file xlsx) | Phân tích 11 mục của báo cáo, chỉ ra các điểm lệch so với đặc tả | Người dùng chốt giữ luật mở rộng và tự vẽ pixel-art |
| 3 | Đặc tả `Campus_Bus_Game_Implementation.md` (luật, trạng thái, 5 hàm, danh sách test) | Lập kế hoạch: viết test trước, logic thuần, rồi đồ họa | Người dùng duyệt kế hoạch |
| 4 | Triển khai theo kế hoạch | 25 test viết trước (ban đầu đỏ), sau đó viết `FinalProject.py` cho đến khi test xanh | Render từng màn hình ra ảnh để kiểm tra bằng mắt và phát hiện lỗi 1–3 |
| 5 | Review code tự động | Phát hiện lỗi 4 | Viết test trước (đỏ), sửa xong thì test xanh |

Công cụ AI: Claude Code (Anthropic).

## Lỗi thật đã gặp và cách sửa

1. **Banner LEVEL hiển thị tốc độ cũ** *(lỗi logic)*
   - Triệu chứng: khi chuyển sang màn 2, ô HUD vẫn ghi `SPEED 100%` trong suốt 1.2 giây hiện banner `LEVEL 2`.
   - Nguyên nhân: `finish_result()` đã tăng `level` nhưng chưa tính lại `speed`. `speed` chỉ được cập nhật trong `start_stop()`, hàm này chạy sau khi banner kết thúc.
   - Cách sửa: tính `"speed": calculate_speed(level + 1)` ngay khi chuyển sang LEVEL_TRANSITION. Đã thêm test hồi quy `test_transition_already_uses_new_level_speed`.
2. **Mặt trời và mặt trăng bị HUD che** *(lỗi bố cục)*: chúng nằm dưới khung Lives/Combo ở (820, 40). Đã dời sang (370, 24) và (330, 110), khoảng trống giữa hai khung HUD.
3. **Chữ "BUS STOP" tràn khỏi biển báo** *(lỗi bố cục)*: biển rộng 72 px không chứa đủ chữ. Đã tăng lên 96 px.
4. **Lệnh thoát bị phím khác ghi đè trong cùng một frame** *(lỗi logic, phát hiện khi review)*
   - Triệu chứng: nếu Esc và Enter (hoặc đóng cửa sổ và R) đến trong cùng một frame, game không thoát mà lại bắt đầu ván mới.
   - Nguyên nhân: `handle_input()` vẫn xử lý tiếp các sự kiện sau khi đã đặt `running = False`. Hàm `new_run()` tạo state mới với `running = True`, nên ghi đè yêu cầu thoát.
   - Cách sửa: dừng vòng lặp sự kiện ngay khi `running` đã là False. Đã thêm test `test_quit_is_not_overridden_by_later_key_in_same_frame`.

## Kết quả kiểm thử

- `python -m unittest discover -s tests`: 27 test, OK.
- Smoke test headless chạy các kịch bản A1–A12 qua hàng đợi sự kiện thật của Pygame: tất cả đạt.
- Mở cửa sổ thật trên macOS khoảng 3 giây, nhấn Enter rồi đóng cửa sổ: thoát sạch.
- Chưa có người chơi thử bằng tay. Cần kiểm tra cảm giác điều khiển và trường hợp giữ Space (A5) trên phím thật.
