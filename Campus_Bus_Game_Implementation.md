# Đặc tả triển khai: Campus Bus Challenge

## 1. Nhiệm vụ dành cho Claude

Hãy triển khai hoàn chỉnh một game desktop 2D bằng Python và Pygame theo tài liệu này. Người chơi căn thời điểm nhấn Space để dừng xe buýt đúng trạm. Game có tăng tốc theo màn, 3 mạng, chấm điểm theo độ chính xác và combo Perfect.

Thực hiện đến khi có game chạy được, kiểm thử các luật chơi và hướng dẫn chạy rõ ràng. Không chỉ đưa ra kế hoạch hoặc đoạn code minh họa. Tự quyết định các chi tiết nhỏ chưa quy định, giữ thiết kế đơn giản và giải thích lựa chọn trong phần bàn giao. Không cần hỏi lại các lựa chọn đã chốt trong tài liệu này.

**Phạm vi chỉ là lập trình game. Chưa viết báo cáo học phần, bài thuyết trình, mã giả hay lưu đồ để nộp.** README hướng dẫn cài đặt/chạy và ghi nhận kiểm thử kỹ thuật vẫn cần có.

## 2. Bối cảnh và ràng buộc

- Đây là dự án cuối kỳ môn Tư duy máy tính, phù hợp sinh viên năm nhất đã học điều kiện, vòng lặp, danh sách và hàm.
- Chỉ phát triển một game; không triển khai các ý tưởng khác trong tài liệu học phần.
- Công nghệ: Python 3.10+ và Pygame 2.x; chọn một phiên bản Pygame đã chạy thử và ghi chính xác trong requirements.txt.
- Chạy offline trên Windows và macOS; không cần server, tài khoản, API hoặc kết nối mạng lúc chơi.
- Không làm web game, không dùng engine khác, không thêm hệ thống vật lý phức tạp.
- Ưu tiên code dễ đọc và giải thích; không xây kiến trúc quá mức cho game nhỏ.
- Bản chơi được phải có đủ đồ họa, không phụ thuộc ảnh/âm thanh chưa được cung cấp.

## 3. Ý tưởng và trải nghiệm

Tên hiển thị: **Campus Bus Challenge**. Tên tiếng Hàn dùng trong mô tả dự án nếu cần: **캠퍼스 셔틀 정차 챌린지**.

Một xe buýt trường học chạy ngang màn hình. Người chơi có một cơ hội nhấn Space trong mỗi lượt để dừng xe. Điểm phụ thuộc khoảng cách giữa tâm xe và tâm vùng dừng. Sau mỗi 3 lượt xử lý trạm, màn tăng và xe chạy nhanh hơn. Người chơi cố sống lâu và đạt điểm cao trước khi mất hết 3 mạng.

Giữ cách chơi một nút, phản hồi nhanh và rõ. Không thêm lái trái/phải, giao thông, hành khách có AI, nhiên liệu, cửa hàng hoặc nhiều loại phương tiện.

## 4. Luật chơi chính xác

### 4.1. Khái niệm

- **Một lượt/trạm:** xe xuất phát ngoài mép trái, chạy về một trạm và kết thúc bằng Perfect, Good, OK hoặc Miss.
- **Một màn:** gồm đúng 3 lượt đã được xử lý. Cả lượt thành công và Miss đều được tính vào 3 lượt; nếu hết mạng thì kết thúc ngay.
- **Một ván:** từ khi bắt đầu cho đến khi số mạng bằng 0. Không giới hạn màn; tốc độ có giới hạn.

### 4.2. Tọa độ và chuyển động

- Kích thước logic mặc định: 1000 × 650 px; mục tiêu 60 FPS.
- Xe nhìn ngang, chạy từ trái sang phải trên một làn đường cố định.
- Kích thước xe tham khảo: 120 × 60 px. Tâm xe ban đầu x = -60, để xe nằm ngoài mép trái.
- Tâm trạm chọn ngẫu nhiên trong đoạn x = 560 đến 800 ở mỗi lượt. Vùng chấm điểm phải nằm trọn trong màn hình.
- Tốc độ màn 1: 260 px/giây.
- Công thức: `speed = min(260 * 1.15 ** (level - 1), 520)`.
- Tính tốc độ có chặn số mũ hoặc cách tương đương để không tràn số khi level rất lớn.
- Dùng delta time cho chuyển động, không dùng số pixel cố định mỗi frame. Chặn delta time tối đa 0.05 giây để tránh bước nhảy lớn khi máy bị giật.
- Nhấn Space thì **dừng ngay**, không có quãng đường phanh hoặc trượt. Hoạt ảnh phản hồi không được làm thay đổi vị trí đã dùng chấm điểm.

### 4.3. Chấm điểm

Đặt `distance = abs(bus_center_x - stop_center_x)` trên tọa độ float hiện tại. Xét các điều kiện theo thứ tự sau:

| Khoảng cách | Xếp loại | Điểm cơ bản | Mạng |
|---|---|---:|---|
| distance ≤ 12 px | Perfect | 100 | Giữ nguyên |
| 12 < distance ≤ 32 px | Good | 60 | Giữ nguyên |
| 32 < distance ≤ 65 px | OK | 30 | Giữ nguyên |
| distance > 65 px | Miss | 0 | Trừ 1 |

- Vẽ vùng ngoài rộng 130 px, vùng Good rộng 64 px và vùng Perfect rộng 24 px, cùng chung tâm; dùng màu và đường tâm để người chơi nhận diện.
- Chấm bằng **tâm xe**, không phải đầu xe hoặc toàn bộ thân xe. Đặt một vạch/chỉ dấu ở giữa thân xe hướng xuống đường để người chơi căn được chính xác.
- Nhấn sớm khi xe chưa vào vùng cũng là Miss; không được nhấn lại để sửa.
- Khi xe đã đi qua biên phải của vùng hợp lệ (`bus_center_x > stop_center_x + 65`) mà chưa nhấn thì tự động Miss, không phải đợi xe ra khỏi màn hình.
- Nếu bước cập nhật làm xe vượt biên thì xử lý Miss đúng một lần. Không cho nhấn muộn để cứu lượt đã được giải quyết.

### 4.4. Combo

- Combo là số Perfect liên tiếp, khởi đầu bằng 0.
- Khi Perfect: tăng combo lên 1 rồi tính thưởng `bonus = min(combo - 1, 5) * 20`.
- Điểm nhận được = 100 + bonus. Lần Perfect đầu là 100, lần hai 120, lần ba 140; từ lần sáu trở đi tối đa 200 điểm/lượt.
- Good, OK hoặc Miss đặt combo về 0.
- Chuỗi Perfect được giữ khi chuyển màn, không reset chỉ vì tăng màn.
- Hiển thị `Perfect!`, `Combo x3` và `+140` khi phù hợp. Chữ x3 chỉ độ dài chuỗi, không có nghĩa nhân điểm với 3.

### 4.5. Mạng và chuyển màn

- Khởi đầu: level = 1, lượt trong màn = 1, score = 0, lives = 3, combo = 0.
- Mỗi Miss trừ đúng 1 mạng. Không có hồi mạng trong phiên bản này.
- Sau mỗi kết quả, giữ phản hồi khoảng 0.9 giây rồi chuyển lượt.
- Sau lượt thứ 3, nếu còn mạng: hiện banner `LEVEL 2` khoảng 1.2 giây rồi bắt đầu lượt 1 màn mới với tốc độ mới. Không cần cộng thêm thời gian phản hồi 0.9 giây vào banner nếu cảm giác bị chậm.
- Nếu mất mạng cuối, chuyển Game Over sau phản hồi ngắn; không tăng màn hoặc tạo lượt mới.
- Sang lượt mới chỉ reset xe, tâm trạm, kết quả và bộ đếm thời gian của lượt; giữ tổng điểm, mạng, level và combo theo quy tắc trên.
- Khi chờ phản hồi hoặc banner, không cho xe chạy và không nhận Space để chấm điểm.

## 5. Điều khiển và trạng thái

| Phím | Hành vi |
|---|---|
| Enter | Bắt đầu ván ở màn hình tiêu đề |
| Space | Dừng xe, chỉ có hiệu lực khi đang chạy |
| P | Tạm dừng/tiếp tục khi đang chạy, đang phản hồi hoặc đang chuyển màn |
| R | Chơi lại từ màn 1 tại Game Over |
| Esc | Thoát game từ bất kỳ trạng thái nào |
| Nút đóng cửa sổ | Thoát sạch từ bất kỳ trạng thái nào |

- Trạng thái tối thiểu: TITLE, PLAYING, RESULT, LEVEL_TRANSITION, PAUSED, GAME_OVER.
- PAUSED cần lưu trạng thái trước đó để quay lại đúng chỗ.
- Trong pause: xe, thời gian chờ, điểm và mọi tiến trình gameplay đứng yên; trở lại không có delta time cộng dồn.
- Chỉ xử lý thao tác theo cạnh nhấn KEYDOWN; không dùng trạng thái giữ Space để liên tục dừng.
- Bảo đảm giữ Space qua nhiều lượt không tự dừng xe ở lượt sau. Tắt key repeat hoặc thêm cơ chế yêu cầu nhả phím trước lượt mới.
- Mỗi lượt chỉ được giải quyết một lần, kể cả có nhiều sự kiện Space trong cùng frame.
- Xử lý event trước cập nhật chuyển động trong mỗi frame, chấm điểm theo vị trí đang hiển thị gần nhất. Chỉ cập nhật chuyển động nếu trạng thái vẫn PLAYING sau xử lý event.

## 6. Giao diện và đồ họa

### 6.1. Phong cách

Đồ họa 2D sạch, tươi sáng, kiểu hoạt hình trường học. Xe vàng nổi bật; nền có tòa nhà trường, cây, mây, mặt đường và nhà chờ xe. Dùng các hình Pygame để tự vẽ, có bố cục và chi tiết hợp lý, tránh chỉ dùng một hình chữ nhật đơn sắc đại diện cho xe.

- Xe có thân, cửa kính, cửa lên xuống, bánh xe và vạch căn tâm.
- Trạm có biển BUS STOP, nhà chờ và vùng căn trên đường.
- Không cần tìm hoặc tải ảnh bên ngoài. Không yêu cầu dịch vụ sinh ảnh.
- Không bắt buộc âm thanh. Nếu thêm âm thanh, tự tạo hoặc kèm tài nguyên hợp lệ, và game vẫn chạy được khi thiết bị âm thanh không khả dụng.
- Dùng tiếng Anh trong UI để tránh phụ thuộc font Hàn/Việt; README và comment có thể bằng tiếng Việt.

### 6.2. Các màn hình

**Title:** tên game, mô tả ngắn, hướng dẫn Space/P/Esc, bảng điểm Perfect/Good/OK, dòng Enter to Start.

**Gameplay:** HUD gồm Score, Level, Stop 1/3, Lives và Combo. Dùng biểu tượng mạng tự vẽ hoặc 3 chấm rõ ràng, không phụ thuộc ký tự emoji. Hiển thị Space to Stop, tốc độ hiện tại hoặc phần trăm so với màn đầu, cùng mục tiêu dừng nổi bật.

**Result:** giữ nguyên vị trí xe để thấy sai lệch; hiện xếp loại, điểm nhận được, khoảng cách lệch và combo nếu có. Miss có phản hồi màu đỏ nhẹ; Perfect có hiệu ứng nhỏ như lóe sáng/confetti. Hiệu ứng không cản đọc hoặc thay đổi logic.

**Level transition:** hiện màn mới và thông báo tốc độ tăng. Khi đã chạm trần tốc độ thì ghi Max Speed, không báo tăng giả.

**Paused:** phủ nền tối và hiện Paused / P to Resume / Esc to Quit.

**Game Over:** tổng điểm, màn đạt được, số lượt đã xử lý, số Perfect, combo cao nhất; R to Retry và Esc to Quit.

### 6.3. Thay đổi khung cảnh

- Màn 1 dùng bảng màu buổi sáng, màn 2 buổi chiều, màn 3 buổi tối; từ màn 4 lặp lại chu kỳ.
- Các vùng chấm điểm và xe luôn có độ tương phản đủ rõ cả trên nền tối.
- Có thể quay bánh xe, chuyển động mây nhẹ và hiệu ứng nút nhấn; không để trang trí làm chậm phần hoàn thiện gameplay.
- Cửa sổ cố định là đủ, không bắt buộc fullscreen hoặc resize.

## 7. Cấu trúc code và dữ liệu

Giữ toàn bộ code gameplay trong một file `FinalProject.py`, thuận tiện đổi thành `MaSinhVien_HoTen_FinalProject.py` khi nộp. Không tự đặt mã sinh viên hoặc họ tên giả.

Bắt buộc có 5 hàm chính sau, với tham số hợp lý do người triển khai lựa chọn:

| Hàm | Trách nhiệm |
|---|---|
| init() | Khởi tạo Pygame, display, clock, font, dữ liệu game |
| handle_input() | Xử lý đóng cửa sổ, phím và chuyển trạng thái do input |
| update_game() | Di chuyển, tự Miss, timer, chuyển lượt và màn |
| render() | Vẽ màn hình tương ứng với trạng thái hiện tại |
| run_game() | Điều phối khởi tạo, event loop, delta time và kết thúc |

Cho phép helper như reset_run(), start_stop(), resolve_stop(), calculate_grade(), calculate_speed(), draw_bus(), draw_background(). Không ép mọi thứ vào 5 hàm quá dài. Dùng dict hoặc dataclass lưu trạng thái, không cần framework nhiều lớp.

Các dữ liệu tối thiểu:

- state, previous_state, running;
- level, stop_index, score, lives, combo, max_combo;
- bus_x dạng float, stop_center_x, speed;
- result_grade, result_points, distance, result_timer, transition_timer;
- total_stops, perfect_count và dữ liệu đồ họa cần thiết.

Các ngưỡng và thời gian phải là hằng số có tên ở đầu file, dễ điều chỉnh. Hàm chấm điểm và tính tốc độ tách khỏi render để dễ kiểm thử. Dùng `if __name__ == '__main__': run_game()` để import không tự mở cửa sổ. Không dùng time.sleep() trong vòng lặp hoặc tạo vòng lặp riêng chặn từng màn hình.

## 8. Sản phẩm phải bàn giao

```text
campus-bus-challenge/
  FinalProject.py
  requirements.txt
  README.md
  tests/
    test_rules.py
```

- Chỉ thêm assets/ nếu thực sự có tài nguyên cần kèm; bản mặc định nên tự vẽ để không cần thư mục này.
- requirements.txt chỉ chứa dependency cần thiết, ưu tiên Pygame là dependency ngoài duy nhất.
- README: giới thiệu ngắn, tạo môi trường ảo, cài dependency, lệnh chạy trên Windows/macOS, phím điều khiển, luật điểm/combo/tốc độ, cách chạy kiểm thử và hạn chế đã biết.
- Dùng unittest tích hợp sẵn cho test_rules.py, không bắt buộc thêm pytest.
- Không cần đóng gói EXE/app, leaderboard online, lưu tài khoản hoặc lưu kỷ lục xuống ổ đĩa.
- Không tạo báo cáo học phần vào lúc này.

## 9. Kiểm thử bắt buộc

### 9.1. Test tự động cho các luật quan trọng

1. Ngưỡng điểm: distance = 0, 12, 12.01, 32, 32.01, 65, 65.01 cho đúng hạng; kiểm tra lệch trái và phải tương đương.
2. Perfect liên tiếp: điểm lần lượt 100, 120, 140, 160, 180, 200, 200; Good/OK/Miss phá combo; Perfect kế tiếp lại được 100.
3. Công thức tốc độ: level 1 = 260, level 2 = 299, các màn cao không vượt 520; màn rất cao không gây overflow.
4. Mỗi lượt chỉ cộng điểm hoặc trừ mạng một lần; sự kiện Space trùng không nhân kết quả.
5. Sau 3 kết quả thì sang màn mới nếu còn mạng; Miss cũng tính một lượt; mất mạng cuối không tạo màn mới.
6. Chơi lại reset điểm, mạng, level, combo và thống kê của ván.

### 9.2. Chạy thử game và kiểm tra tương tác

| Mã | Tình huống | Kết quả cần đạt |
|---|---|---|
| A1 | Mở game và nhấn Enter | Bắt đầu màn 1, 3 mạng, 0 điểm |
| A2 | Nhấn Space đúng vùng | Xe đứng yên, hạng và điểm đúng vị trí |
| A3 | Nhấn Space quá sớm | Miss, mất đúng 1 mạng |
| A4 | Không nhấn phím | Vượt tâm trạm + 65 thì tự Miss một lần |
| A5 | Giữ hoặc bấm Space liên tục | Không chấm nhiều lần, không tự dừng lượt mới |
| A6 | Hoàn thành 3 lượt, còn mạng | Màn tăng, lượt về 1/3, tốc độ đúng công thức |
| A7 | Perfect qua ranh giới màn | Combo được giữ và tính tiếp |
| A8 | Mất mạng cuối ở lượt 3 | Game Over, không sang màn mới |
| A9 | Pause ở PLAYING/RESULT/LEVEL_TRANSITION | Chuyển động và timer dừng, resume đúng trạng thái |
| A10 | Nhấn R ở Game Over | Ván mới hoàn toàn, không giữ thống kê cũ |
| A11 | Esc hoặc đóng cửa sổ ở mọi trạng thái | Thoát sạch, không treo |
| A12 | Màn sáng/chiều/tối và tốc độ tối đa | Chữ/vùng mục tiêu rõ, game vẫn chơi được |

Chạy kiểm thử tự động và mở game thực tế nếu môi trường có giao diện. Nếu chỉ có môi trường headless, dùng smoke test phù hợp và nêu rõ phần tương tác/đồ họa chưa được kiểm chứng. Không tuyên bố đã chơi thử khi chỉ chạy test logic. Sửa lỗi tìm được trước khi bàn giao.

## 10. Trình tự triển khai và tiêu chí hoàn thành

1. Kiểm tra thư mục dự án hiện tại, bảo toàn code có sẵn nếu có; tạo thư mục riêng nếu đang ở workspace chung.
2. Làm đầy đủ state machine và gameplay trước: chuyển động, chấm điểm, combo, mạng, màn, pause và restart.
3. Hoàn thiện đồ họa, HUD, phản hồi kết quả và đổi cảnh.
4. Viết các kiểm thử có ý nghĩa, chạy game, sửa lỗi, bổ sung README.
5. Bàn giao đường dẫn file, lệnh chạy, kết quả kiểm thử thực tế và hạn chế còn lại.

Chỉ coi là hoàn thành khi game chạy độc lập sau khi cài requirements, mọi luật bắt buộc đã được triển khai, không có TODO chặn gameplay, không có tài nguyên bị thiếu và không có tính năng giả. Không mở rộng phạm vi trước khi các tiêu chí này đạt.
