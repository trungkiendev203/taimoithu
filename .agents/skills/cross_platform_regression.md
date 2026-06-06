---
name: cross_platform_regression
description: Mandatory regression testing after any bug fix.
triggers:
  - bug
  - bug fix
  - fix
  - debug
  - error
  - exception
  - issue
  - broken
  - not working
  - regression
priority: critical
always_apply: true
---

# Cross Platform Regression Verification

## CRITICAL RULE

Nếu nhiệm vụ có chứa bất kỳ từ khóa nào:

- fix
- bug
- debug
- error
- issue
- exception
- broken
- not working
- regression

THÌ PHẢI KÍCH HOẠT SKILL NÀY NGAY LẬP TỨC.

Không được tiếp tục xử lý cho đến khi toàn bộ quy trình trong skill được thực hiện.

## Mục tiêu

Đảm bảo sau khi sửa bất kỳ lỗi nào, agent phải tự động kiểm tra các hệ thống liên quan và chỉ kết thúc khi xác nhận toàn bộ chức năng hoạt động bình thường.

## Quy tắc bắt buộc

Khi nhận yêu cầu sửa lỗi:

1. Phân tích nguyên nhân gốc (Root Cause).
2. Thực hiện sửa lỗi.
3. Chạy lại chức năng vừa sửa để xác nhận lỗi đã được khắc phục.
4. Tự động tìm tất cả module, service, API, page, workflow hoặc nền tảng khác có khả năng bị ảnh hưởng.
5. Thực hiện regression test trên các thành phần liên quan.
6. Nếu phát hiện lỗi mới:
   - Tiếp tục sửa.
   - Kiểm tra lại toàn bộ.

7. Chỉ được kết thúc khi tất cả bài kiểm tra đều PASS.

## Cross-Platform Verification

Nếu lỗi xuất hiện trên một nền tảng:

- YouTube → kiểm tra TikTok, Facebook, Instagram và các nguồn video khác.
- Website → kiểm tra API liên quan.
- API → kiểm tra tất cả client đang sử dụng API.
- Mobile → kiểm tra Android, iOS và Backend liên quan.
- Database → kiểm tra tất cả chức năng đọc/ghi dữ liệu liên quan.

## Completion Criteria

Không được báo "đã sửa xong" cho đến khi:

- Root cause được xác định.
- Fix được áp dụng.
- Regression test hoàn tất.
- Không còn lỗi liên quan.
- Các nền tảng liên quan hoạt động bình thường.

## Reporting Format

Root Cause:
...

Files Modified:
...

Validation Results:
...

Regression Tests:
...

Final Status:
PASS / FAIL

## Optimization

- Ưu tiên hành động thay vì giải thích dài dòng.
- Giảm tối đa token sử dụng.
- Không lặp lại thông tin.
- Không dừng sau khi sửa lỗi.
- Luôn thực hiện regression test trước khi kết thúc.
