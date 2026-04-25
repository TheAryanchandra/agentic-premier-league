# Stadium Experience Dashboard - 45 Min Build

## Project Structure
```
stadium-dashboard/
├── backend/
│   ├── main.py              (FastAPI app - 150 lines)
│   ├── requirements.txt      (Dependencies)
│   ├── Dockerfile           (Cloud Run config)
│   └── .env.example         (Firebase credentials)
├── frontend/
│   ├── index.html           (Single HTML file - React)
│   ├── src/
│   │   ├── App.jsx          (Main component)
│   │   ├── Dashboard.jsx    (Dashboard view)
│   │   └── firebase.js      (Firebase config)
│   └── package.json         (NPM config)
└── README.md                (Setup instructions)
```

## ⏱️ Timeline (45 mins)

| Time | Task | Duration |
|------|------|----------|
| 0-5 min | Clone & Setup | 5 min |
| 5-15 min | Firebase Setup | 10 min |
| 15-25 min | Backend Deploy | 10 min |
| 25-40 min | Frontend Build & Test | 15 min |
| 40-45 min | Final Deploy | 5 min |

## Features You Get

✅ Live crowd density dashboard (Real-time Firestore sync)
✅ Zone-wise color-coded density (Green/Yellow/Red)
✅ Historical 30-min trends
✅ Staff admin panel (update crowd counts)
✅ Alert system for emergencies
✅ Mobile-responsive web dashboard
✅ Deployed on Cloud Run

## Prerequisite (5 mins)

- Google Cloud Account (with $5 credit)
- Firebase Project (create in console)
- Git installed
- Node.js installed
