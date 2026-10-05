# Nghiên cứu learning science và quyết định cho repo

Ngày kiểm tra: **2026-10-05**. [Báo cáo chính và danh mục nghiên cứu](../../research/learning-science-review.md) giữ citation/DOI; [access log](../../research/source-checks.json) ghi trạng thái từng nguồn. Đây là tổng hợp có phê bình nhưng **chưa hoàn thành xác minh nghiên cứu gốc**, không phải systematic review mới.

## Phương pháp và giới hạn

Chọn tài liệu theo nhóm phương pháp, ưu tiên review/meta-analysis, nghiên cứu gốc và tổng hợp học thuật. Không tìm kiếm toàn diện, preregister, double screening, đánh giá risk-of-bias hay publication-bias. Proxy từ chối DOI (403); không tìm cách vượt policy. Đã đọc trực tiếp bản **Deans for Impact (2015), The Science of Learning**, gồm bibliography, và các episode practice/memory/feedback/teaching của The Carpentries tại commit `50745001271700a108de0622d80341965e249e5b`.

Đây là nguồn tổng hợp giảng dạy uy tín, không thay thế xem phương pháp, heterogeneity và độ trễ của meta-analysis. Đối tượng Carpentries thường là người mới học công cụ tính toán; áp dụng sang CS sau đại học vẫn cần đánh giá. Không nhận nguyên cách nói mạnh như “dạy người khác là một trong những cách tốt nhất”. Không đưa effect size chưa kiểm chứng. Productive failure và mastery learning đặc biệt là khuyến nghị thiết kế tạm thời vì chưa đọc được meta-analysis đã chọn.

[PDF đã đọc](https://github.com/carpentries/instructor-training/blob/50745001271700a108de0622d80341965e249e5b/episodes/files/papers/science-of-learning-2015.pdf), câu hỏi 1–4 nối prerequisite, ví dụ mẫu, spacing/retrieval, interleaving, feedback theo task và transfer cấu trúc với nghiên cứu được trích. [Memory](https://github.com/carpentries/instructor-training/blob/50745001271700a108de0622d80341965e249e5b/episodes/05-memory.md), [practice](https://github.com/carpentries/instructor-training/blob/50745001271700a108de0622d80341965e249e5b/episodes/02-practice-learning.md), [feedback](https://github.com/carpentries/instructor-training/blob/50745001271700a108de0622d80341965e249e5b/episodes/06-feedback.md) đã đọc trực tiếp.

## Mức bằng chứng và hoạt động hằng ngày

“Được hỗ trợ rộng” nghĩa là nguyên tắc hội tụ trong văn liệu và phù hợp nguồn tổng hợp đọc được, không chứng nhận mọi task/effect. “Phụ thuộc bối cảnh” nghĩa là thiết kế, nền tảng, feedback/control thay đổi kết quả. “Heuristic” là lựa chọn sản phẩm có thể sửa và cần đo.

| Phương pháp / mức tin cậy | Phù hợp / áp dụng / hạn chế | Hoạt động và đo hiệu quả |
|---|---|---|
| Retrieval — hỗ trợ rộng cho retention; transfer có điều kiện | Definition, invariant, phân biệt concept, tái dựng reasoning/procedure. Thử không ghi chú rồi corrective feedback; tránh high stakes mọi lần, cue đáp án hoặc lặp misconception chưa sửa; mới học có thể cần được dạy trước | Tái dựng invariant, dự đoán query/chọn thuật toán; lưu response/hint/error. Kiểm tra prompt khác sau độ trễ, tách accuracy cùng ngày khỏi retention |
| Spacing — hỗ trợ rộng; interval tùy điều kiện | Knowledge/procedure cần giữ nhiều tuần. Phân bố practice, xét retention horizon/nền/task; không có lịch tối ưu phổ quát, không dồn backlog vào phiên ngắn | Tạo prompt sau completion/attempt thật, thay due theo recall có lý do. Đo delay thật, success, hint, quá hạn và độ khó tương đương |
| Interleaving — phụ thuộc bối cảnh | Phân biệt BFS/Dijkstra, seek/scan, lower/upper bound. Có initial blocked practice trước khi mix; không đổi course ngẫu nhiên gây switching cost | Chọn strategy trước khi giải và nêu feature quyết định. Đo lựa chọn/justification ở case mới sau delay, tách correctness code |
| Self-explanation — có văn liệu hỗ trợ, phụ thuộc task | Causal reasoning, proof, quyết định trong ví dụ, debug. Prompt “vì sao bước này”; kiểm tra explanation sai dù trôi chảy; tránh quá tải novice | Giải thích update giữ invariant, cho counterexample. Rubric mechanism/assumption/counterexample/trade-off; giải thích boundary mới sau delay |
| Elaboration — phụ thuộc nền tảng | Nối idea mới với cấu trúc đã biết, analogy có giới hạn. Tránh story trang trí/analogy chưa kiểm tra | Nối partition với time-window query và điểm analogy dừng. Đo connection đúng và áp dụng ngữ cảnh mới, không lặp chuyện |
| Worked example/scaffolding/fading — hỗ trợ novice, expertise reversal có điều kiện | Procedure nhiều bước, proof, tool lạ. Một ví dụ nêu quyết định rồi bỏ dần bước; expert có thể cần independent sớm, tránh guidance dư | Trace → implementation thiếu bước → range query độc lập → record/key mới. Đo giảm hint mà giữ correctness case mới và reconstruction sau delay |
| Deliberate practice — phụ thuộc domain/định nghĩa | Subskill có chuẩn và corrective feedback. Target lỗi đã chẩn đoán, variation có mục đích; code mỗi ngày không tự là deliberate practice, giờ học không là mastery clock | Minimal counterexample off-by-one, sửa và case đổi. Đo recurrence, debug explanation, độc lập/tái làm sau delay |
| Feedback/misconception repair — mục đích được hỗ trợ, timing/content có điều kiện | Lỗi mental model, procedure/API. Feedback cụ thể sau attempt, sửa và reattempt; hint sớm có thể spoil retrieval, feedback setup muộn gây lãng phí | “Rule bỏ duplicate đầu, trace `[2,2]`”; sửa invariant rồi case mới. Lưu lỗi gốc, correction, explanation và lần thử sau delay |
| Cognitive load — framework có nền, intervention tùy bối cảnh | Novice gặp đồng thời concept/tool/reasoning mới. Giảm setup dư, chunk, explanation cạnh code; effort không là phép đo dung lượng trí nhớ | Starter offline, một invariant, checkpoint, không ép Docker. Tách friction/time khỏi conceptual error, effort và kết quả sau delay; nhẹ hơn chưa chắc học tốt hơn |
| Productive failure — phụ thuộc bối cảnh, tạm thời ở review này | Người có nền thử problem sinh nhiều phương án rồi explicit consolidation. Time-box và debrief; tránh mò mẫm khi nền yếu | Predict duplicate boundary, thử rule, đối chiếu counterexample/ví dụ; novice xem ví dụ trước. Đo alternatives và transfer sau instruction; không thưởng mastery vì struggle |
| Transfer — phụ thuộc bối cảnh, far transfer khó | Áp cấu trúc sang data/constraint/representation khác. Nhiều case so cấu trúc rõ; một task không chứng minh engineering expertise | Timestamp window, record/key; tách array khỏi B-tree/update cost. Đo near/changing-context riêng và thử lại sau delay không hint |
| Mastery/adaptation — phụ thuộc bối cảnh, tạm thời | Mục tiêu giới hạn, diagnostic, corrective instruction và reassessment. Rubric trước practice; không có universal 65/85% gate, completion không mastery | Low → sửa lỗi; cùng ngày độc lập → provisional; recall/transfer ngày sau → bằng chứng mạnh hơn. Lưu interval/task/hint và uncertainty |

## Văn liệu cần kiểm tra tiếp

Bản chính ghi rõ nguồn nào có bibliography trong PDF đã đọc và nguồn nào là candidate cần xác minh. DOI đã thử ngày 2026-10-05 nhưng không đọc được full text: Dunlosky et al. 2013 (broad review), Rowland 2014 (testing meta-analysis), Cepeda et al. 2006 (spacing quantitative synthesis), Brunmair & Richter 2019 (interleaving moderators), Bisra et al. 2018 (self-explanation meta-analysis), Atkinson et al. 2000 (worked-example review), Renkl et al. 2002 (fading experiment), Macnamara et al. 2014 (deliberate-practice meta-analysis), Shute 2008 (feedback review), Sweller 1988 (load), Sinha & Kapur 2021 (productive-failure meta-analysis), Kulik et al. 1990 (mastery meta-analysis). Ericsson 1993, *How People Learn* 2000 và *Education for Life and Work* 2012 có trong bibliography nhưng chưa fetch riêng.

Các citation này không chứng minh đã đọc methods. Cần quyền truy cập học thuật để hoàn tất verification trước khi claim effect chính xác.

## Khuyến nghị đã triển khai

1. Lifecycle và assessment có bằng chứng thay generation-as-progress; score/explanation chưa biết giữ null.
2. Một core objective, cho review-only/prerequisite repair; time mode là heuristic sản phẩm.
3. Ví dụ → lab → independent → transfer, hint tăng dần, lời giải tách mentor.
4. Completion khác mastery; independent cùng ngày provisional. Ngày sau là tối thiểu quan sát của schema ngày, không phải retention horizon đủ về khoa học.
5. Lịch ôn sau quan sát, giữ từng attempt và lý do đổi due. +1/+3/+7/+21 hay nhân đôi chỉ là heuristic tùy chọn; fail cần correction/retry phù hợp, success cân nhắc interval dài theo mục tiêu.
6. Đo vài tuần bằng delayed performance, hint, recurrence, explanation và transfer với difficulty/delay. Trend trước/sau không chứng minh nhân quả vì workload/familiarity/topic là confounder.
7. Stars chỉ metadata discovery; pin lát cắt implementation/test, ghi việc xác minh thật.

Xem [workflow](../references/learning-workflow.md), [bài mẫu](../lessons/boundary-search/lesson.md) và [review repo](repository-review.md).

Nguồn đọc thêm: [runtime review](runtime-design-review.md) ghi practice guide IES/WWC 2007 và evidence ratings. Candidate paper trước vẫn chưa full-text verified; đọc guide mới không thay việc đọc chúng.
