📌 Project Overview

Automated AOI (Automated Optical Inspection) Defect Tracking System for PCBAs.

Extracts, processes, and analyzes AOI machine log files in real-time.

Designed to reduce scrap rate and improve production quality monitoring.

🚀 Features

Real-time Log Parsing – Reads AOI logs every 15 minutes.

Defect Classification – Tracks Missing, Out Polarity, Bridging, and Upside-down defects.

Database Integration – Stores parsed data into SQL Server for persistence.

Dashboard & Analytics – Interactive visualization of defect trends, operator performance, and pass/fail ratios.

Error Flagging – Automatically marks NG (Not Good) PCBAs with error codes.

Barcode & Image Mapping – Each record linked with barcode, picName, and picPath for traceability.

Historical & Real-Time Insights – Compare trends across shifts/days to find recurring defect patterns.

🛠️ Tech Stack

Python (Pandas, Regex, Logging, OS, Threading)

SQL Server (Data storage, querying defect trends)

Visualization – Matplotlib / Plotly / Power BI / Tableau (depending on what you used)

Automation – Scheduled parsing for continuous monitoring
