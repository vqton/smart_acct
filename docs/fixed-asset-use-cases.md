# Use Case Specification

## 1. Source
- URL 1: https://ketoanthienung.net/tai-san-co-dinh-la-gi.htm (Tổng quan TSCĐ)
- URL 2: https://ketoanthienung.net/tai-san-co-dinh-huu-hinh.htm (TSCĐ hữu hình)
- URL 3: https://ketoanthienung.net/tai-san-co-dinh-vo-hinh.htm (TSCĐ vô hình)
- URL 4: https://ketoanthienung.net/tai-san-co-dinh-thue-tai-chinh.htm (TSCĐ thuê tài chính)
- URL 5: https://ketoanthienung.net/dau-tu-nang-cap-sua-chua-tai-san-co-dinh.htm (Nâng cấp, sửa chữa TSCĐ)

---

## 2. Domain Breakdown

### Domain: FIXED_ASSET_REGISTRATION (Đăng ký & Ghi nhận TSCĐ)

#### UC-01: Recognize Fixed Asset

- **Goal:** Ghi nhận một tài sản là TSCĐ khi đáp ứng đủ tiêu chuẩn
- **Actors:** Kế toán viên, Trưởng phòng kế toán
- **Preconditions:** Tài sản đã được mua/xây dựng/xuất hiện tại DN
- **Trigger:** Tài sản mới được đưa vào sử dụng
- **Main Flow:**
  1. Kiểm tra 3 tiêu chuẩn bắt buộc:
     - Lợi ích kinh tế chắc chắn trong tương lai
     - Thời gian sử dụng > 1 năm
     - Nguyên giá ≥ 30.000.000 VND
  2. Nếu tài sản hữu hình → phân loại vào 1 trong 7 nhóm (nhà cửa, máy móc, phương tiện vận tải, thiết bị quản lý, vườn cây/súc vật, kết cấu hạ tầng, loại khác)
  3. Nếu tài sản vô hình → xác định loại (quyền SD đất, bằng sáng chế, bản quyền, phần mềm, nhãn hiệu...)
  4. Xác định nguyên giá ban đầu
  5. Ghi nhận vào sổ TSCĐ (TK 211/213)
- **Alternate Flow:** Tài sản không đủ tiêu chuẩn → hạch toán là CCDC hoặc chi phí trong kỳ
- **Exception Flow:** Tài sản do Nhà nước giao/cấp không thu tiền → không ghi nhận TSCĐ vô hình
- **Output:** Biên bản giao nhận TSCĐ (mẫu 01-TSCĐ), thẻ TSCĐ
- **Dependencies:** Quy định tại TT 45/2013/TT-BTC Điều 3

#### UC-02: Determine Original Cost (Nguyên giá)

- **Goal:** Xác định nguyên giá TSCĐ theo từng hình thức hình thành
- **Actors:** Kế toán viên
- **Preconditions:** TSCĐ đã được nhận diện
- **Trigger:** Khi ghi nhận TSCĐ
- **Main Flow:**
  1. Xác định hình thức hình thành TSCĐ:
     - Mua sắm (mới/cũ) → giá mua + thuế (không hoàn lại) + CP vận chuyển, lắp đặt, chạy thử, lệ phí trước bạ, lãi vay trong quá trình đầu tư
     - Tự xây dựng/sản xuất → giá quyết toán công trình / giá thành thực tế
     - Đầu tư XDCB → giá quyết toán + lệ phí trước bạ + CP liên quan
     - Trao đổi → giá trị hợp lý của tài sản nhận về
     - Được cấp/biếu/tặng → giá trị đánh giá của Hội đồng giao nhận
     - Nhận góp vốn → giá trị do các bên thỏa thuận / tổ chức định giá
     - Mua trả chậm → giá mua trả tiền ngay (không gồm lãi trả chậm)
  2. Tính tổng các chi phí hợp lý
  3. Ghi nhận nguyên giá vào sổ kế toán
- **Alternate Flow:** Mua nhà cửa gắn với quyền SD đất → tách riêng giá trị đất (TSCĐ vô hình) và nhà (TSCĐ hữu hình)
- **Exception Flow:** TSCĐ đã sử dụng nhưng chưa quyết toán → ghi nhận giá tạm tính, điều chỉnh sau
- **Output:** Nguyên giá TSCĐ được ghi nhận
- **Dependencies:** TT 45/2013/TT-BTC Điều 4, 5

#### UC-03: Classify Fixed Asset by Purpose

- **Goal:** Phân loại TSCĐ theo mục đích sử dụng
- **Actors:** Kế toán viên
- **Preconditions:** TSCĐ đã được ghi nhận
- **Trigger:** Khi phân loại/quản lý TSCĐ
- **Main Flow:**
  1. Xác định mục đích sử dụng:
     - Kinh doanh (chính)
     - Phúc lợi, sự nghiệp, an ninh, quốc phòng
     - Bảo quản hộ, giữ hộ
  2. Ghi nhận vào nhóm tương ứng
- **Output:** Phân loại TSCĐ trong sổ sách
- **Dependencies:** TT 45/2013/TT-BTC Điều 6

---

### Domain: FIXED_ASSET_DEPRECIATION (Khấu hao TSCĐ)

#### UC-04: Calculate Depreciation

- **Goal:** Tính và trích khấu hao TSCĐ hàng kỳ
- **Actors:** Kế toán viên
- **Preconditions:** TSCĐ đã ghi nhận và đưa vào sử dụng
- **Trigger:** Cuối mỗi kỳ kế toán (tháng/quý/năm)
- **Main Flow:**
  1. Xác định thời gian trích khấu hao (theo khung quy định hoặc dự tính của DN)
  2. Chọn phương pháp khấu hao: đường thẳng, số dư giảm dần, sản lượng
  3. Tính số khấu hao kỳ này
  4. Phân bổ vào chi phí SXKD theo bộ phận sử dụng
  5. Ghi nhận hao mòn lũy kế (TK 214)
- **Alternate Flow:** TSCĐ chưa sử dụng → không trích khấu hao (trừ một số trường hợp đặc thù)
- **Exception Flow:** TSCĐ thuê tài chính cam kết không mua lại → khấu hao theo thời hạn thuê
- **Output:** Bảng tính và phân bổ khấu hao TSCĐ (mẫu 06-TSCĐ)
- **Dependencies:** TT 45/2013/TT-BTC Điều 9, 10, 11

#### UC-05: Register Depreciation Method

- **Goal:** Đăng ký phương pháp trích khấu hao với cơ quan thuế
- **Actors:** Kế toán viên, Giám đốc
- **Preconditions:** DN có TSCĐ
- **Trigger:** Khi bắt đầu năm tài chính hoặc khi có TSCĐ mới
- **Main Flow:**
  1. Lựa chọn phương pháp khấu hao phù hợp
  2. Lập bảng đăng ký phương pháp trích khấu hao
  3. Trình Giám đốc phê duyệt
  4. Lưu hồ sơ
- **Output:** Bảng đăng ký phương pháp trích khấu hao TSCĐ
- **Dependencies:** TT 45/2013/TT-BTC

---

### Domain: FINANCE_LEASE (Thuê tài chính TSCĐ)

#### UC-06: Record Finance Lease Asset

- **Goal:** Ghi nhận TSCĐ thuê tài chính
- **Actors:** Kế toán viên
- **Preconditions:** Hợp đồng thuê tài chính đã ký
- **Trigger:** Khi nhận tài sản thuê
- **Main Flow:**
  1. Xác định hợp đồng thuê tài chính (thỏa mãn ≥1/3 điều kiện: chuyển giao quyền sở hữu, giá mua thấp hơn giá trị hợp lý, thời hạn thuê chiếm phần lớn thời gian SD)
  2. Xác định nguyên giá = giá trị hợp lý hoặc giá trị hiện tại của khoản thanh toán tiền thuê tối thiểu
  3. Ghi nhận TSCĐ thuê tài chính (TK 212)
  4. Ghi nhận nợ thuê tài chính (TK 3412)
  5. Xử lý thuế GTGT đầu vào (khấu trừ hoặc không khấu trừ)
- **Alternate Flow:** Hợp đồng không thỏa mãn điều kiện thuê tài chính → phân loại là thuê hoạt động
- **Output:** Bút toán ghi nhận TSCĐ thuê tài chính
- **Dependencies:** TT 45/2013/TT-BTC Điều 3, 4, 8; TT 133/2016 hoặc TT 99/2025

#### UC-07: Pay Finance Lease Installment

- **Goal:** Thanh toán tiền thuê định kỳ
- **Actors:** Kế toán viên, Thủ quỹ
- **Preconditions:** Hợp đồng thuê tài chính đang hiệu lực
- **Trigger:** Đến kỳ thanh toán
- **Main Flow:**
  1. Xác định số tiền gốc và lãi trong kỳ
  2. Ghi nhận lãi thuê vào chi phí tài chính (TK 635)
  3. Ghi giảm nợ gốc (TK 3412)
  4. Thanh toán cho bên cho thuê
- **Output:** Bút toán trả nợ thuê tài chính
- **Dependencies:** Hợp đồng thuê tài chính

#### UC-08: Transfer Ownership at Lease End

- **Goal:** Xử lý TSCĐ thuê tài chính khi kết thúc hợp đồng
- **Actors:** Kế toán viên
- **Preconditions:** Hợp đồng thuê tài chính kết thúc
- **Trigger:** Khi hết hạn hợp đồng
- **Main Flow:**
  1. Nếu mua lại tài sản: chuyển từ TK 212 → TK 211, chuyển hao mòn từ TK 2142 → TK 2141
  2. Nếu trả lại tài sản: ghi giảm TK 212 và TK 2142
- **Output:** Bút toán chuyển đổi/trả lại TSCĐ
- **Dependencies:** Hợp đồng, quyết định mua lại

---

### Domain: FIXED_ASSET_MAINTENANCE (Sửa chữa & Nâng cấp TSCĐ)

#### UC-09: Record Repair Cost

- **Goal:** Hạch toán chi phí sửa chữa TSCĐ
- **Actors:** Kế toán viên
- **Preconditions:** TSCĐ phát sinh hư hỏng cần sửa chữa
- **Trigger:** Khi có hóa đơn/chứng từ sửa chữa
- **Main Flow:**
  1. Xác định đây là sửa chữa (duy tu, bảo dưỡng, khôi phục trạng thái ban đầu)
  2. Chi phí sửa chữa → hạch toán trực tiếp hoặc phân bổ dần vào chi phí SXKD
  3. Thời gian phân bổ tối đa không quá 3 năm
- **Alternate Flow:** Sửa chữa có tính chu kỳ → DN trích trước chi phí theo dự toán hàng năm
- **Exception Flow:** Chi thực tế > dự toán → tính thêm chênh lệch; chi thực tế < dự toán → giảm chi phí
- **Output:** Bút toán chi phí sửa chữa TSCĐ
- **Dependencies:** TT 45/2013/TT-BTC Điều 7

#### UC-10: Record Upgrade Cost

- **Goal:** Hạch toán chi phí nâng cấp TSCĐ
- **Actors:** Kế toán viên
- **Preconditions:** TSCĐ cần nâng cấp (cải tạo, mở rộng, nâng công suất)
- **Trigger:** Khi hoàn thành nâng cấp
- **Main Flow:**
  1. Xác định đây là nâng cấp (tăng công suất, chất lượng, tính năng, kéo dài thời gian SD)
  2. Chi phí nâng cấp → ghi tăng nguyên giá TSCĐ
  3. Không hạch toán vào chi phí SXKD trong kỳ
- **Output:** Bút toán tăng nguyên giá TSCĐ
- **Dependencies:** TT 45/2013/TT-BTC Điều 7

---

### Domain: FIXED_ASSET_INVENTORY (Kiểm kê & Xử lý TSCĐ)

#### UC-11: Conduct Fixed Asset Inventory

- **Goal:** Kiểm kê TSCĐ định kỳ
- **Actors:** Kế toán viên, Ban kiểm kê
- **Preconditions:** Đến kỳ kiểm kê (cuối năm hoặc đột xuất)
- **Trigger:** Yêu cầu kiểm kê
- **Main Flow:**
  1. Thành lập Hội đồng kiểm kê
  2. Đối chiếu thực tế với sổ sách
  3. Phát hiện thừa/thiếu TSCĐ
  4. Lập biên bản kiểm kê (mẫu 05-TSCĐ)
- **Output:** Biên bản kiểm kê TSCĐ
- **Dependencies:** Chế độ kế toán DN

#### UC-12: Dispose / Liquidate Fixed Asset

- **Goal:** Thanh lý TSCĐ (hết khấu hao hoặc chưa hết khấu hao)
- **Actors:** Kế toán viên, Giám đốc, Hội đồng thanh lý
- **Preconditions:** TSCĐ không còn sử dụng được / hết thời gian SD
- **Trigger:** Quyết định thanh lý
- **Main Flow:**
  1. Thành lập Hội đồng thanh lý
  2. Lập biên bản thanh lý (mẫu 02-TSCĐ)
  3. Xuất hóa đơn thanh lý (xác định thuế suất)
  4. Ghi nhận thu nhập/chi phí thanh lý (TK 711/811)
  5. Xóa sổ TSCĐ (giảm nguyên giá, giảm hao mòn lũy kế)
- **Output:** Biên bản thanh lý, hóa đơn, bút toán xóa sổ
- **Dependencies:** TT 45/2013/TT-BTC, Luật thuế GTGT

#### UC-13: Transfer / Sell Fixed Asset

- **Goal:** Nhượng bán TSCĐ
- **Actors:** Kế toán viên, Giám đốc
- **Preconditions:** TSCĐ được phép nhượng bán
- **Trigger:** Quyết định nhượng bán
- **Main Flow:**
  1. Định giá tài sản
  2. Xuất hóa đơn
  3. Ghi nhận thu nhập (TK 711) và chi phí (TK 811)
  4. Xóa sổ TSCĐ
- **Output:** Hợp đồng mua bán, hóa đơn, bút toán
- **Dependencies:** TT 45/2013/TT-BTC

#### UC-14: Revaluate Fixed Asset

- **Goal:** Đánh giá lại giá trị TSCĐ
- **Actors:** Kế toán viên, Hội đồng định giá
- **Preconditions:** Có yêu cầu đánh giá lại (sáp nhập, chia tách, cổ phần hóa)
- **Trigger:** Yêu cầu từ cấp quản lý/hội đồng quản trị
- **Main Flow:**
  1. Thành lập Hội đồng đánh giá
  2. Xác định giá trị còn lại thực tế
  3. Lập biên bản đánh giá lại (mẫu 04-TSCĐ)
  4. Điều chỉnh chênh lệch vào vốn chủ sở hữu hoặc thu nhập/chi phí
- **Output:** Biên bản đánh giá lại TSCĐ
- **Dependencies:** Chuẩn mực kế toán, quy định pháp luật

---

### Domain: FIXED_ASSET_REPORTING (Báo cáo TSCĐ)

#### UC-15: Generate Depreciation Schedule

- **Goal:** Lập bảng tính và phân bổ khấu hao TSCĐ
- **Actors:** Kế toán viên
- **Preconditions:** Có số liệu khấu hao các kỳ
- **Trigger:** Cuối mỗi kỳ kế toán
- **Main Flow:**
  1. Tổng hợp số khấu hao từng TSCĐ trong kỳ
  2. Phân bổ chi phí khấu hao cho từng bộ phận
  3. Lập bảng tính (mẫu 06-TSCĐ)
- **Output:** Bảng tính và phân bổ khấu hao TSCĐ
- **Dependencies:** Số liệu khấu hao từng TSCĐ

#### UC-16: Record Fixed Asset Transfer (Handover)

- **Goal:** Lập biên bản bàn giao TSCĐ (mới mua, sửa chữa lớn xong)
- **Actors:** Kế toán viên, Bên giao, Bên nhận
- **Preconditions:** TSCĐ sẵn sàng bàn giao
- **Trigger:** Khi tiếp nhận TSCĐ mới hoặc sau sửa chữa lớn
- **Main Flow:**
  1. Lập biên bản bàn giao (mẫu 01-TSCĐ)
  2. Xác nhận của các bên
  3. Cập nhật thẻ TSCĐ
- **Output:** Biên bản giao nhận TSCĐ
- **Dependencies:** Chứng từ mua hàng / nghiệm thu sửa chữa

#### UC-17: Generate Fixed Asset Reports

- **Goal:** Lập báo cáo tổng hợp về TSCĐ
- **Actors:** Kế toán viên, Kế toán trưởng
- **Preconditions:** Số liệu TSCĐ đã được cập nhật đầy đủ
- **Trigger:** Cuối kỳ kế toán (tháng/quý/năm)
- **Main Flow:**
  1. Tổng hợp nguyên giá, hao mòn, giá trị còn lại
  2. Lập báo cáo TSCĐ theo yêu cầu quản trị và thuế
  3. Trình kế toán trưởng và giám đốc
- **Output:** Báo cáo TSCĐ (phục vụ BCTC và quản trị)
- **Dependencies:** Bảng khấu hao, sổ TSCĐ

---

## 3. Cross-Use Case Observations

### Overlapping use cases
- **UC-01 (Recognize)** và **UC-02 (Determine Cost)** luôn đi cùng nhau: ghi nhận TSCĐ đồng thời xác định nguyên giá
- **UC-04 (Depreciation)** và **UC-15 (Depreciation Schedule)** là hai mặt của cùng một quy trình: tính khấu hao và lập báo cáo
- **UC-12 (Liquidate)**, **UC-13 (Sell)**, và **UC-14 (Revaluate)** đều kết thúc vòng đời TSCĐ — cần thống nhất quy trình xóa sổ
- **UC-09 (Repair)** và **UC-10 (Upgrade)** có ranh giới mờ: cùng một chi phí, phân loại sai → ảnh hưởng nguyên giá TSCĐ

### Flows bị thiếu / rời rạc
- **Luân chuyển TSCĐ nội bộ** (giữa các phòng ban, chi nhánh) — không được đề cập trong nguồn
- **Bảo hiểm TSCĐ** — không có quy trình quản lý bảo hiểm tài sản
- **Cho thuê hoạt động TSCĐ** — được nhắc đến nhưng không có UC riêng
- **TSCĐ đi thuê hoạt động** — chỉ được đề cập là "không phải thuê tài chính"
- **Trích trước chi phí sửa chữa có chu kỳ** — flow mờ, thiếu chi tiết hạch toán

### Điểm không rõ
- Tiêu chí phân biệt rõ giữa "sửa chữa" và "nâng cấp" trong thực tế — dễ gây nhầm lẫn, hậu quả thuế khác nhau
- Cách xử lý TSCĐ vô hình tự tạo từ nội bộ (điều kiện 7 tiêu chí) — quy trình kiểm tra không chi tiết

---

## 4. Gaps Identified

### Missing use cases
1. **UC-Missing-01: Register Fixed Asset Transfer Between Departments** — điều chuyển TSCĐ nội bộ giữa các bộ phận
2. **UC-Missing-02: Insure Fixed Asset** — mua và theo dõi bảo hiểm TSCĐ
3. **UC-Missing-03: Record Operating Lease (Lessee)** — quy trình thuê hoạt động bên đi thuê
4. **UC-Missing-04: Record Operating Lease (Lessor)** — quy trình cho thuê hoạt động bên cho thuê
5. **UC-Missing-05: Handle Self-Constructed Intangible Asset** — kiểm tra 7 điều kiện ghi nhận TSCĐ vô hình tự tạo
6. **UC-Missing-06: Handle Asset Found Surplus/Deficit** — xử lý thừa/thiếu TSCĐ sau kiểm kê

### Missing validation
- **Nguyên giá 30 triệu** — không có validation chéo giữa giá mua và tổng chi phí
- **Phân loại tài sản** — không có cơ chế kiểm tra tính nhất quán giữa mục đích sử dụng và tài khoản hạch toán
- **Thời gian khấu hao** — không có validation đối chiếu với khung thời gian quy định

### Missing error handling
- **Nhập sai loại tài sản** (hữu hình ↔ vô hình) — không có cơ chế sửa sai
- **Hạch toán sai sửa chữa ↔ nâng cấp** — ảnh hưởng đến nguyên giá và chi phí thuế TNDN
- **Thuế GTGT đầu vào TSCĐ** — không có quy trình xử lý khi thuế GTGT bị từ chối khấu trừ

---

## 5. Suggested Improvements

### Process improvements
1. **Tách rõ UC-09 và UC-10**: Bổ sung decision tree để phân biệt "sửa chữa" vs "nâng cấp" dựa trên tiêu chí:
   - Có tăng công suất/ chất lượng/ tính năng so với ban đầu? → Nâng cấp
   - Có kéo dài thời gian sử dụng? → Nâng cấp
   - Không → Sửa chữa (bảo dưỡng, duy tu, khôi phục)

2. **Validation chéo giữa đăng ký phương pháp khấu hao và thực tế trích khấu hao**: Cảnh báo nếu lệch.

3. **Quy trình kiểm tra 7 điều kiện TSCĐ vô hình tự tạo**: Checklist rõ ràng cho từng điều kiện.

### System features
1. **TSCĐ Dashboard**: Hiển thị tổng quan nguyên giá, hao mòn, giá trị còn lại theo từng nhóm
2. **Cảnh báo thời gian khấu hao sắp kết thúc**: Notification khi TSCĐ sắp hết khấu hao
3. **Tự động phân bổ chi phí sửa chữa > 3 năm**: Cảnh báo nếu thời gian phân bổ vượt quy định
4. **Audit trail cho thay đổi nguyên giá**: Ghi lại lịch sử thay đổi nguyên giá (sửa chữa, nâng cấp, đánh giá lại)
5. **Tích hợp với hóa đơn điện tử**: Tự động đề xuất hạch toán khi nhận hóa đơn mua TSCĐ
