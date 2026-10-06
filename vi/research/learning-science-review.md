# Learning science cho ngày học kỹ thuật sâu

Kiểm tra **2026-10-06**. Phạm vi: tự học Computer Science, lập trình và thí nghiệm kỹ thuật, prerequisite chưa rõ và nộp bài tùy chọn. Đây là review tập trung có giới hạn truy cập rõ, **không phải systematic review hoặc đánh giá hiệu quả giáo dục của tutor này**. Không có thí nghiệm mới hay effect size định lượng được tuyên bố.

## Đã kiểm tra gì

Tìm kiếm tập trung retrieval, spacing, interleaving, examples, deliberate practice, feedback và cognitive load. Nguồn ứng viên từ publisher học thuật, repo tác giả/trường, PubMed và practice guide dựa bằng chứng. Đọc các phần liên quan để nối claim với hoạt động. Không có search đăng ký trước, screening đầy đủ, đánh giá risk of bias độc lập hay reanalysis. Bằng chứng nền tảng cũ hữu ích nhưng không trả lời mọi task lập trình hiện đại.

[Log chung](../../research/deep-study-source-checks.json) có URL, timestamp, HTTP, bytes, hash, phạm vi đọc và giới hạn. Sáu nguồn có full text và **đã đọc một số phần**; ba nguồn **chỉ đọc abstract**; một publisher ứng viên không truy cập được. Tải thành công không là review toàn paper. [Log trước](../../research/source-checks.json) giữ lịch sử; proxy từ chối trước không mô tả kết quả truy cập hôm nay.

| Nguồn/truy cập | Phần đọc | Giới hạn còn lại |
|---|---|---|
| [Dunlosky và cộng sự (2013)](https://iverson.cm.utexas.edu/courses/310M/Handouts/Dunlosky%20et%20al.%20-%202013%20-%20Improving%20Students%E2%80%99%20Learning%20With%20Effective%20Learni.pdf), publisher PDF lưu tại trường, HTTP 200 | Summary, retrieval implementation/assessment, spacing, cautions interleaving, utility table | Chọn section; không audit độc lập từng thí nghiệm gốc |
| [Cepeda và cộng sự (2006)](https://escholarship.org/content/qt3rr6q10c/qt3rr6q10c_noSplash_2440ea21aa88b3b0722b0afa9171f88b.pdf), repo học thuật, HTTP 200 | Abstract, introduction, search/methods và coding khoảng cách | Author manuscript có thể khác bản cuối; chủ yếu verbal recall |
| [Shute (2008)](https://myweb.fsu.edu/vshute/pdf/shute%202008_b.pdf), PDF tác giả, HTTP 200 | Abstract, introduction/method, guidelines và timing feedback | Một số phần của review có task/population đa dạng |
| [Ericsson, Krampe và Tesch-Römer (1993)](https://blogs.ischool.berkeley.edu/i225s14/files/2014/04/Ericsson-1993-article.pdf), PDF tại trường, HTTP 200 | Định nghĩa practice, feedback/resources, thiết kế nhóm nhạc công | Expertise/âm nhạc, không là thử nghiệm đào tạo lập trình |
| [Sweller, van Merriënboer và Paas (2019)](https://link.springer.com/article/10.1007/s10648-019-09465-5), full text publisher, HTTP 200 | Examples, split attention, expertise reversal và fading | Framework/review, đọc chọn lọc, không quy tắc phổ quát |
| [Pashler và cộng sự (2007), IES/WWC](https://ies.ed.gov/ncee/WWC/Docs/PracticeGuide/20072004.pdf), HTTP 200 | Bảng evidence, scope và guidance spacing/examples/quizzing/explanations | Chính cho lớp 3–12, có bàn liên quan đại học; không thử agent tutoring |
| [Rowland (2014)](https://pubmed.ncbi.nlm.nih.gov/25150680/), PubMed HTTP 200 | Abstract/meta-analysis và thư mục | Chưa đọc full methods/moderators |
| [Brunmair và Richter (2019)](https://pubmed.ncbi.nlm.nih.gov/31556629/), PubMed HTTP 200 | Abstract meta-analysis interleaving | Chưa đọc full methods; web reader fail nhưng executor thành công |
| [Macnamara, Hambrick và Oswald (2014)](https://pubmed.ncbi.nlm.nih.gov/24986855/), PubMed HTTP 200 | Abstract và notice corrigendum 2018 | Chưa đọc correction/full methods; không dùng claim định lượng |
| [Atkinson và cộng sự (2000)](https://journals.sagepub.com/doi/10.3102/00346543070002181), publisher HTTP 403 | Chỉ metadata từ search | Không tính full text đã đọc; policy examples dùng nguồn truy cập được ở trên |

Browser service timeout ở publisher Dunlosky, trả 429/fetch fail với một số trang metadata. HTTPS từ executor qua proxy kế thừa sau đó lấy được bản học thuật/abstract. Log ghi riêng hai kết quả; không vượt giới hạn truy cập.

## Finding và lựa chọn dạy

Nghiên cứu hỗ trợ các nguyên tắc chung có giới hạn task/population. Cột cuối là **suy luận thiết kế của project**, không là intervention các paper đã thử.

| Phương pháp | Nguyên tắc và giới hạn | Hoạt động kỹ thuật |
|---|---|---|
| Retrieval | Review Dunlosky/abstract Rowland hỗ trợ retrieval thay vì chỉ restudy; learning/transfer phụ thuộc task | Tự tái dựng invariant/dự đoán output không notes, xem đáp án rồi sửa model |
| Spacing | Synthesis Cepeda nối gap hữu ích với mục tiêu lưu giữ; không xác định mốc phổ quát | Trace lại ngày sau, ghi delay/hint thật, chỉnh prompt theo khó khăn quan sát |
| Interleaving | Abstract Brunmair cho thấy phụ thuộc loại material; trộn tùy tiện không có căn cứ | Sau học ban đầu, so chiến lược liên quan và giải thích lựa chọn trước code |
| Worked examples | Review Sweller nói lợi ích cho novice, tích hợp thông tin và giảm hỗ trợ theo expertise | Trace giải thích → điền phần còn thiếu → biến thể độc lập mới, giải thích cạnh code |
| Luyện có mục đích/deliberate | Ericsson mô tả cải thiện đúng điểm yếu có theo dõi; abstract Macnamara cảnh báo giải thích expertise chỉ bằng practice | Tách kiểu bug đã thấy, tạo phản ví dụ nhỏ, sửa/thử case mới; code thường không là bằng chứng |
| Feedback | Shute đề nghị sửa cụ thể theo task, timing tùy ngữ cảnh | So response thật với tiêu chí, giải thích lệch, hướng sửa và case mới |
| Cognitive load | Sweller bàn tải từ phần tử tương tác/expertise; cảm giác effort không đo trực tiếp capacity | Bớt setup, ghép code/sơ đồ với giải thích, giảm scaffolding dư |

IES guide độc lập nối spacing, worked solution/problem solving, retrieval và câu hỏi giải thích với khuyến nghị, nhưng mức evidence khác nhau. Không chứng nhận mọi phương pháp ngang nhau hay lịch tutor bảy giờ. Self-explanation dùng để xem suy luận; nói trôi chảy mà sai vẫn phải sửa. Transfer được thử rõ, không suy từ cùng test case.

## Quyết định project, không là tối ưu khoa học

Theo yêu cầu, thiết kế **6–8 giờ tổng**, mặc định **420 phút = 360 học + 60 nghỉ**, **235 phút chủ động (65,3% phút học)**. Tối thiểu 60% phút học là kỹ thuật chủ động. Các số này phục vụ ưu tiên thực hành, có thể chỉnh lại. Review không tìm ra liều học/nghỉ/tỷ lệ tối ưu. Ngày có nhiều loại hoạt động và nghỉ, không tuyên bố bảy giờ deliberate practice liên tục là phù hợp.

[Template](../references/lesson-template.md) xác định lịch: orient/retrieve 20; model/worked trace 50; nghỉ 10; source research 45; implementation trace 45; trưa 30; lab/debug 75; nghỉ 10; controlled experiment 45; nghỉ 10; transfer 35; tổng hợp 45. Đọc thụ động, xem, setup và nghỉ không tính active. Bridge self-check thay đào sâu; setup có fallback giới hạn; câu hỏi phụ dời sau. Thời gian ngắn yêu cầu rõ ghi đè default.

Mỗi ngày một objective, outcome hỗ trợ nhỏ, câu hỏi research giới hạn, artifact tái hiện và checkpoint. Research tạo claim ledger; experiment ghi hypothesis, variable, controls, seed/cases, result/limits. Benchmark chỉ đúng workload/môi trường, không xếp implementation phổ quát.

Bản EN/VI đầy đủ với objective, code, sources, lệnh, experiment/lời giải tương đương. Đường chỉ đọc và đáp án có ngay; không nộp vẫn học ngày mai. Tỷ lệ thực hành mô tả **đường full-day được cung cấp**, không ép người chọn đường chỉ đọc.

## Contract kiến thức và evidence

Tách background tự khai, evidence đã quan sát, unknown/unverified và misconception thật. Kinh nghiệm lập trình giúp chọn ví dụ, không là assessment thuật toán/toán. Agent tests kiểm artifact, không proficiency người học. Đọc/xem đáp án không tạo mastery/completion.

Completion khác proficiency: schema v3 cần assessment đủ loại/cùng topic/đúng lifecycle. Tutor kiểm thêm **objective → task → rubric → evidence**, vì topic equality không chứng minh liên hệ. Ghi trợ giúp; đã xem đáp án thì đánh giá independent dùng biến thể mới. Completion có thể đi cùng needs_support. Repair cần evidence fresh/independent/non-exit phù hợp; lỗi gốc vẫn giữ.

Independent cùng ngày là tạm thời. Recall không hint sau delay và transfer có ý nghĩa tăng confidence trong đúng phạm vi. Ngày sau chỉ là độ trễ tối thiểu quan sát, không là mastery bền vững. Lịch/độ khó là heuristic theo kết quả/retention goal, không mốc phổ quát.

## Đánh giá thiết kế

Theo dõi vài tuần: accuracy sau delay, giải thích, lệ thuộc hint, misconception lặp, performance đổi ngữ cảnh, với độ khó và delay thật. Ghi riêng setup, workload và mệt tự khai. Không gọi before/after không kiểm soát là nhân quả: quen task, workload, topic có thể giải thích trend.

Tests repo kiểm state/linkage/privacy/tái hiện; review song ngữ kiểm parity; scenarios skill mô tả hành vi mong muốn. Tests kỹ thuật hay file scenario chưa chạy không chứng minh model tuân thủ hoặc người học tiến bộ. Claim giáo dục mạnh hơn cần outcome người học thật và thiết kế so sánh phù hợp.

Contracts: [pedagogy](../references/pedagogy.md), [workflow](../references/learning-workflow.md), [source policy](../references/source-policy.md), [template](../references/lesson-template.md), [agent skill](../../skills/cs-daily-deep-study/SKILL.md), [ví dụ full-day](../lessons/2026-10-05-cost-model/lesson.md).
