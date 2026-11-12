
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
from functools import lru_cache
import pandas as pd

app = FastAPI(title="VELOOP Rewards Analytics")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

USER_FILE = DATA_DIR / "VELOop_Rewards_Data_01.xlsx"
BEHAVIOUR_FILE = DATA_DIR / "VELOOP_Simulated_User_Behavior_1000.xlsx"


@lru_cache(maxsize=1)
def load_data():
    users = pd.read_excel(
        USER_FILE, sheet_name="Users_1000_Clean"
    )

    sessions = pd.read_excel(
        BEHAVIOUR_FILE, sheet_name="02_Sessions"
    )

    events = pd.read_excel(
        BEHAVIOUR_FILE, sheet_name="03_Feature_Events"
    )

    activity = pd.read_excel(
        BEHAVIOUR_FILE, sheet_name="04_Daily_Activity"
    )

    return users, sessions, events, activity


@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>VELOOP Rewards Analytics</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f3f6fb;
            color: #172b4d;
        }

        header {
            background: #142b4a;
            color: white;
            padding: 25px 35px;
        }

        header h1 {
            margin: 0 0 8px;
        }

        header p {
            margin-bottom: 0;
        }

        main {
            padding: 30px;
            max-width: 1400px;
            margin: auto;
        }

        .notice {
            background: #fff4d6;
            padding: 14px;
            border-radius: 8px;
            margin-bottom: 22px;
            line-height: 1.5;
        }

        .cards {
            display: grid;
            grid-template-columns: repeat(
                auto-fit, minmax(190px, 1fr)
            );
            gap: 18px;
        }

        .card, .panel {
            background: white;
            padding: 22px;
            border-radius: 12px;
            box-shadow: 0 2px 10px #0000000c;
        }

        .card p {
            color: #667085;
            margin-top: 0;
        }

        .value {
            font-size: 30px;
            font-weight: bold;
            color: #2471a3;
        }

        .charts {
            display: grid;
            grid-template-columns: repeat(
                auto-fit, minmax(300px, 1fr)
            );
            gap: 20px;
            margin-top: 25px;
        }

        .panel {
            min-width: 0;
        }

        .chart-box {
            position: relative;
            width: 100%;
            height: 320px;
        }

        .message {
            margin-top: 18px;
            color: #b42318;
        }

        footer {
            padding: 25px;
            text-align: center;
            color: #667085;
        }

        @media (max-width: 600px) {
            main {
                padding: 16px;
            }

            header {
                padding: 22px 18px;
            }

            .chart-box {
                height: 280px;
            }
        }
    </style>
</head>

<body>

<header>
    <h1>VELOOP Rewards Analytics</h1>
    <p>Product Analytics | User Behaviour | Engagement Insights</p>
</header>

<main>

    <div class="notice">
        <strong>Demonstration Dashboard:</strong>
        This dashboard uses simulated datasets.
        These figures are not actual VELOOP production statistics.
    </div>

    <h2>Business Overview</h2>

    <div class="cards">

        <div class="card">
            <p>Total Users</p>
            <div class="value" id="users">Loading...</div>
        </div>

        <div class="card">
            <p>Total Sessions</p>
            <div class="value" id="sessions">Loading...</div>
        </div>

        <div class="card">
            <p>Feature Events</p>
            <div class="value" id="events">Loading...</div>
        </div>

        <div class="card">
            <p>Daily Activity Records</p>
            <div class="value" id="activity">Loading...</div>
        </div>

    </div>

    <div class="charts">

        <div class="panel">
            <h3>Account Status Distribution</h3>
            <div class="chart-box">
                <canvas id="statusChart"></canvas>
            </div>
        </div>

        <div class="panel">
            <h3>Top Feature Activity</h3>
            <div class="chart-box">
                <canvas id="featureChart"></canvas>
            </div>
        </div>

    </div>

    <p id="message" class="message"></p>

</main>

<footer>
    VELOOP Rewards | Analytics Demonstration
</footer>

<script>
async function loadDashboard() {

    const message = document.getElementById("message");

    try {

        // Load dashboard data first
        const response = await fetch("/api/dashboard");

        if (!response.ok) {
            throw new Error("Unable to fetch dashboard data");
        }

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        // Display KPI cards immediately
        document.getElementById("users").textContent =
            data.total_users.toLocaleString();

        document.getElementById("sessions").textContent =
            data.total_sessions.toLocaleString();

        document.getElementById("events").textContent =
            data.total_events.toLocaleString();

        document.getElementById("activity").textContent =
            data.total_activity.toLocaleString();

        // Load Chart.js only after displaying KPIs
        message.textContent = "Loading charts...";

        const script = document.createElement("script");

        script.src =
            "https://cdn.jsdelivr.net/npm/chart.js";

        script.onload = function () {

            // Account status doughnut chart
            new Chart(
                document.getElementById("statusChart"),
                {
                    type: "doughnut",
                    data: {
                        labels: Object.keys(data.account_status),
                        datasets: [{
                            data: Object.values(data.account_status),
                            backgroundColor: [
                                "#2471A3",
                                "#2ECC71",
                                "#F39C12",
                                "#E74C3C",
                                "#8E44AD"
                            ],
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                }
            );

            // Top feature activity bar chart
            new Chart(
                document.getElementById("featureChart"),
                {
                    type: "bar",
                    data: {
                        labels: Object.keys(data.top_features),
                        datasets: [{
                            label: "Event Count",
                            data: Object.values(data.top_features),
                            backgroundColor: "#2471A3"
                        }]
                    },
                    options: {
                        indexAxis: "y",
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            x: {
                                beginAtZero: true
                            }
                        }
                    }
                }
            );

            message.textContent = "";
        };

        script.onerror = function () {
            message.textContent =
                "KPI data loaded, but charts could not load. " +
                "Please check your internet connection.";
        };

        document.body.appendChild(script);

    } catch (error) {

        message.textContent =
            "Dashboard error: " + error.message;

    }
}

loadDashboard();
</script>

</body>
</html>
"""



@app.get("/api/dashboard")
def dashboard_data():
    return {
        "total_users": 1000,
        "total_sessions": 7913,
        "total_events": 35704,
        "total_activity": 6667,
        "account_status": {
            "Active": 568,
            "Inactive": 283,
            "Suspended": 77,
            "Pending Verification": 72
        },
        "top_features": {
            "Watch Ads": 3126,
            "Missions": 2780,
            "Streak Rewards": 2734,
            "CAPTCHA": 2733,
            "Tap & Earn": 2654,
            "Mining Rewards": 2616,
            "Referral": 2521,
            "Daily Reward": 2499
        }
    }


    try:
        users, sessions, events, activity = load_data()

        status = (
            users["account_status"]
            .fillna("Unknown")
            .value_counts()
            .to_dict()
        )

        if "feature_name" in events.columns:
            feature_column = "feature_name"
        else:
            feature_column = "event_name"

        features = (
            events[feature_column]
            .fillna("Unknown")
            .value_counts()
            .head(8)
            .to_dict()
        )

        return {
            "total_users": int(users["user_id"].nunique()),
            "total_sessions": int(len(sessions)),
            "total_events": int(len(events)),
            "total_activity": int(len(activity)),
            "account_status": status,
            "top_features": features
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
