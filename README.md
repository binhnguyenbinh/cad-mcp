# ClaudeCAD

ClaudeCAD (Claude AI cho AutoCAD, phiên bản 3.1.1) là một palette trong AutoCAD để trò chuyện với Claude AI. Bạn gõ yêu cầu bằng tiếng Việt hoặc tiếng Anh, Claude đọc và sửa bản vẽ đang mở.

## Chức năng

- Trò chuyện với Claude ngay trong AutoCAD, ra lệnh để Claude vẽ hoặc sửa bản vẽ.
- Hỏi về bản vẽ, ví dụ liệt kê layer, đổi màu đối tượng, viết một đoạn lệnh.
- Làm việc với nhiều bản vẽ; mỗi bản vẽ có hội thoại riêng.
- Đính kèm ảnh, PDF, tệp văn bản và Excel vào câu hỏi; chụp một vùng màn hình và đưa vào palette.
- Mỗi lượt Claude sửa bản vẽ được gom thành một bước hoàn tác (Undo).
- Tạo và nạp skill để dạy Claude làm việc lặp lại (xem mục Skill).

## Yêu cầu

- Windows 10 bản 1809 trở lên, hoặc Windows 11, máy 64-bit.
- AutoCAD 2018 trở lên. Không hỗ trợ AutoCAD LT.
- Tài khoản Claude hoặc API key.
- Kết nối Internet. Không cần Claude Desktop.

## Cài đặt

1. Chạy `cad-mcp-setup-3.1.1.exe`. Nếu Windows hiện "Windows protected your PC", bấm **More info** rồi **Run anyway**.
2. Đóng AutoCAD trước khi cài. Nếu Setup báo AutoCAD đang chạy, đóng AutoCAD rồi bấm **Retry**.
3. Đánh dấu ô "Tôi hiểu rủi ro trên và chỉ dùng palette với bản vẽ, tệp tin cậy" để bấm **Tiếp**.
4. Cài cho người dùng hiện tại, không cần quyền quản trị. Nếu Setup không tự cài được Claude Code, làm theo hướng dẫn chính thức của Anthropic.
5. Mở AutoCAD, chọn **Always Load** nếu được hỏi có nạp ClaudeCAD không. Mở palette bằng lệnh `CLAUDE`, hoặc tab **Add-ins** trên Ribbon rồi bấm **Claude AI**.

## Cách dùng

- **Đăng nhập** (trong **Cài đặt**): **Tài khoản Claude** (mặc định) thì chọn **Đăng nhập Claude** khi Setup hỏi, hoặc gõ `/login` trong palette. **API key** thì nhập bằng nút **Dán & lưu**; key được mã hoá và lưu trên máy này. Đăng nhập báo lỗi 403 nghĩa là tổ chức đang chặn Claude Code; liên hệ quản trị viên CNTT.
- **Gửi yêu cầu**: gõ trong ô chat, **Enter** để gửi, **Shift+Enter** xuống dòng, **Esc** dừng Claude. Ví dụ: "Liệt kê các layer trong bản vẽ này", "Đổi màu các đối tượng này sang đỏ".
- **Mới** bắt đầu hội thoại sạch, không còn ngữ cảnh cũ. Gợi ý trong `goi_y.txt`: bấm đúp để gửi luôn.
- **Mẹo**: **Model** và **Mức suy nghĩ** (trong Cài đặt): mức cao trả lời kỹ hơn nhưng chậm, câu hỏi nhanh nên chọn low hoặc medium. Bật **Kèm đối tượng chọn** để gửi kèm đối tượng đang chọn trong AutoCAD. Phím chụp vùng Ctrl+Shift+X và ẩn/hiện palette Ctrl+5 chỉ hoạt động khi AutoCAD ở phía trước; nếu Ctrl+Shift+X làm UniKey đổi kiểu gõ, đổi sang Ctrl+Shift+Q trong Cài đặt. Trước khi gửi, kiểm tra đúng bản vẽ đang hoạt động. Đính kèm bằng kéo thả hoặc Ctrl+V, tối đa 10 tệp và 15 MB mỗi tin nhắn.
- **An toàn**: Claude tự chạy lệnh AutoCAD và mã trên máy với quyền của bạn, không hỏi lại. Chỉ dùng với bản vẽ và tệp tin cậy, lưu bản vẽ trước khi dùng, và đọc kỹ kết quả trước khi lưu. Bản vẽ, yêu cầu và tệp đính kèm được gửi tới Anthropic. Chữ trong bản vẽ có thể chứa chỉ dẫn giả; khi chuyển sang việc khác, bấm **Mới**.

## Skill

Skill là tệp `SKILL.md` hướng dẫn Claude cách làm một việc lặp lại trong AutoCAD.

Trong **Cài đặt**, dòng **Skill** hiện trạng thái (chưa có skill, số skill, hoặc đang tắt). Bấm **Quản lý ▾** để mở menu:

- **Mở thư mục skill**: mở thư mục skill trong Explorer.
- **Tạo skill mới**: tạo mẫu skill và mở bằng Notepad để bạn sửa.
- **Nạp skill…**: chọn tệp SKILL.md hoặc gói .zip; palette hiện hộp xác nhận trước khi chép.

Gọi skill bằng `/tên-skill nội dung cần làm`. Có thể nhờ Claude soạn skill trong khung chat; bản nháp chỉ được nạp sau khi bạn đọc và xác nhận. Chỉ nạp skill từ nguồn tin cậy. Skill có thể hướng Claude chạy lệnh và mã trên máy bạn.

## Gỡ cài đặt

Đóng AutoCAD, rồi vào **Start Menu** → **Claude AI cho AutoCAD** → **Gỡ cài đặt Claude AI cho AutoCAD**. Skill và `goi_y.txt` của bạn được giữ lại.

## Hướng dẫn chi tiết

Xem `installer\docs\HDSD.html`.

## Giấy phép

Phần mềm được phát hành theo giấy phép MIT. Copyright (c) 2026 Gaus. Xem tệp `LICENSE`.

## Hermes / MCP (vẽ AutoCAD qua MCP)

`server.py` là MCP server (stdio) nói chuyện với AutoCAD đang mở qua COM. Hermes Agent chỉ cần đăng ký trong `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  autocad:
    command: "C:/Users/<user>/AppData/Local/hermes/installs/<install>/environments/<env>/venv/Scripts/python.exe"
    args: ["D:/project/cad-mcp/server.py"]
    timeout: 120
```

Restart Hermes, các tool `mcp_autocad_*` (line, circle, rectangle, text, layer, save, screenshot, run_python, ...) sẽ xuất hiện. AutoCAD phải đang mở và không ở trạng thái busy (đóng dialog "Drawing Recovery" nếu có).

Smoke test: `python -I -B tests/test_mcp_smoke.py` (AutoCAD phải đang mở) → 9/9 pass.
