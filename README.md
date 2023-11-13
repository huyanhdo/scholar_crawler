## Project for crawl CSIRO data 

CSIRO Crawler is a tool for crawling expert information and patent information


## Task Google Scholar 
Từ danh sách các link 
-> crawl all (trong này đã tất cả hàm util crawl tên, bài viết)
-> trích xuất tên tổ chức, coauthor -> crawl expert liên quan 
-> Lọc người Việt 
-> Kết quả 
Update: 
Lấy danh sách expert đã crawl -> crawl lại -> nếu phát hiện thay đổi thì update (crawl fail thì k update)
Crawl new: 
Lấy danh sách các expert mới (bỏ những expert đã crawl) -> crawl all -> tạo mới trong db 
-> lưu vào db riêng 
-> trích xuất db riêng và tự update 