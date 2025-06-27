import base64
from datetime import datetime, timedelta
import streamlit as st
import requests
from collections import Counter
import pandas as pd
import webbrowser
import json
import plotly.express as px

#  centralized constants
API_ENDPOINT = "https://api.github.com/graphql"
DEFAULT_AVATAR = "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"

# error handling decorator
def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            st.error(f"🔌 Network error: {str(e)}")
        except json.JSONDecodeError:
            st.error("❌ Invalid API response")
        except Exception as e:
            st.error(f"⚠️ Unexpected error: {str(e)}")
    return wrapper

# fix_json_values with type hints
def fix_json_values(json_to_fix: dict) -> dict:
    """Convert boolean/None values to human-readable strings"""
    conversions = {
        "False": "No",
        "None": "Not Available", 
        "True": "Yes"
    }
    return {k: conversions.get(str(v), v) for k, v in json_to_fix.items()}

# data fetching
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_most_used_languages(token: str, name: str, appendRender: bool = True):
    """Fetch user's most used programming languages"""
    headers = {"Authorization": f"Bearer {token}"}
    query = """{
      user(login: "%s") {
        repositories(first: 100) {
          nodes {
            languages(first: 100) {
              nodes {
                name
              }
            }
          }
        }
      }
    }""" % name

    try:
        response = requests.post(API_ENDPOINT, json={"query": query}, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        language_counts = Counter()
        for repo in data["data"]["user"]["repositories"]["nodes"]:
            for language in repo["languages"]["nodes"]:
                language_counts[language["name"]] += 1

        most_common = language_counts.most_common(5)
        df_languages = pd.DataFrame(most_common, columns=["Language", "Count"])

        if appendRender:
            st.subheader("Most Used Languages")
            st.bar_chart(df_languages.set_index("Language"))
        else:
            return [lang[0] for lang in most_common]

    except Exception as e:
        st.error(f"Error fetching languages: {e}")
        return [] if not appendRender else None

@handle_errors
def get_user_info(token: str, name: str):
    """Fetch and display comprehensive user statistics"""
    query = f"""query {{
        user(login: "{name}") {{
            name
            email
            avatarUrl
            bio
            createdAt
            location
            websiteUrl
            publicRepos: repositories(isFork: false, privacy: PUBLIC) {{
                totalCount
            }}
            privateRepos: repositories(isFork: false, privacy: PRIVATE) {{
                totalCount
            }}
            pullRequests {{
            totalCount
            }}
            contributionsCollection {{
                totalCommitContributions
                totalIssueContributions
                totalPullRequestContributions 
                contributionCalendar {{
                    totalContributions
                    weeks {{
                        contributionDays {{
                            date
                            contributionCount
                            weekday
                        }}
                    }}
                }}
            }}
            issues {{
                totalCount
            }}
        }}
    }}"""

    headers = {"Authorization" : f"Bearer{token}"}

    try:
        response = requests.post(
            API_ENDPOINT,
            headers=headers,
            json={"query": query},
        )
        response.raise_for_status()
        data = response.json()
        user_data = data.get("data", {}).get("user", {})

        stats = {
            "public_repos": user_data.get('publicRepos', {}).get('totalCount', 0),
            "private_repos": user_data.get('privateRepos', {}).get('totalCount', 0),
            "total_contributions": user_data.get('contributionsCollection', {}).get('contributionCalendar', {}).get('totalContributions', 0),
            "issues": user_data.get('issues', {}).get('totalCount', 0),
            "pull_requests": user_data.get('pullRequests', {}).get('totalCount', 0),
            "commits": user_data.get('contributionsCollection', {}).get('totalCommitContributions', 0)
            }
                 
# improved visualization
            # profile header
        with st.container():
            cols = st.columns([1, 4])
            with cols[0]:
                st.image(user_data.get('avatarUrl', DEFAULT_AVATAR), width=100)
                
            with cols[1]:
                st.subheader(user_data.get('name', 'N/A'))
                if user_data.get('bio'):
                    st.caption(user_data['bio'])
                st.caption(f"📍 {user_data.get('location', 'Not specified')}")

            # stats cards
            st.subheader("📊 Activity Overview")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Public Repos", stats['public_repos'])
            col2.metric("Private Repos", stats['private_repos'])
            col3.metric("Total Contributions", stats['total_contributions'])
            col4.metric("Issues Created", stats['issues'])
            
            # enhanced charts
            # 1. Repo Distribution Pie Chart
            fig_repos = px.pie(
                names=['Public', 'Private'],
                values=[stats['public_repos'], stats['private_repos']],
                title="Repository Distribution",
                hole=0.4,
                color_discrete_sequence=['#1f6feb', '#58a6ff']  # GitHub colors
            )
            fig_repos.update_traces(textposition='inside', textinfo='percent+label')
            
            # 2. Contributions Heatmap
            contrib_data = []
            weeks = user_data.get('contributionsCollection', {}).get('contributionCalendar', {}).get('weeks', [])
            for week in weeks:
                for day in week.get("contributionDays", []):
                    contrib_data.append({
                        "Date": day["date"],
                    "Contributions": day["contributionCount"],
                    "Day": day["weekday"]
                })
                    
        df_contrib = pd.DataFrame(contrib_data)
        if not df_contrib.empty:
            df_contrib["Date"] = pd.to_datetime(df_contrib["Date"])
            fig_heatmap = px.density_heatmap(
                df_contrib,
                x="Day",
                y=df_contrib["Date"].dt.strftime("%Y-W%V"),
                z="Contributions",
                color_continuous_scale="blues"
        )
        fig_heatmap.update_layout(title="Contribution Heatmap")
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
            # 3. Activity Bar Chart
        activity_data = {
            "Type": ["Commits", "PRs", "Issues"],
            "Count": [stats['commits'], stats['pull_requests'], stats['issues']]
        }
        fig_activity = px.bar(
            activity_data,
            x="Type",
            y="Count",
            color="Type",
            title="Activity Breakdown",
            color_discrete_sequence=['#1f6feb', '#58a6ff', '#2ea043']
        )
        
        # Display all charts
        st.plotly_chart(fig_repos, use_container_width=True)
        st.plotly_chart(fig_activity, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error fetching user info: {str(e)}")
        if st.toggle("Show details"):
             st.exception(e)
                
                # repo functions                                
def fetch_custom_commit_history(selected_repo, name, token):
    """Get detailed commit history for a specific repository"""
    headers = {"Authorization": f"Bearer {token}"}

    query = """
    {
        repository(owner: "%s", name: "%s") {
            defaultBranchRef {
                target {
                    ... on Commit {
                        history {
                            totalCount
                            nodes {
                                oid
                                message
                                committedDate
                            }
                        }
                    }
                }
            }
        }
    }
    """ % (name, selected_repo)

    try:
        response = requests.post(API_ENDPOINT, json={"query": query}, headers=headers)
        response.raise_for_status()
        data = response.json()

        commit_nodes = data["data"]["repository"]["defaultBranchRef"]["target"]["history"]["nodes"]
        return {
            "OID": [commit["oid"] for commit in commit_nodes],
            "Message": [commit["message"] for commit in commit_nodes],
            "Date": [commit["committedDate"] for commit in commit_nodes],
            "Commit Count": list(range(1, len(commit_nodes) + 1))
        }

    except Exception as e:
        print(e)
        st.error(f"bro, see error: {e}")
        return 

@handle_errors
def fetch_commit_history(token, name, num_days):
    """Show commit activity over time"""
    st.title("Your last commits (details)")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    query = """
    {
      user(login: "%s") {
        contributionsCollection(from: "%sT00:00:00Z", to: "%sT23:59:59Z") {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """ % (name, (datetime.now() - timedelta(days=num_days)).date(), datetime.now().date())

    try:
        response = requests.post(API_ENDPOINT, headers=headers, json={"query": query})
        response.raise_for_status()
        data = response.json()

        contributions = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        commit_data = pd.DataFrame(
            [
                (datetime.strptime(day["date"], "%Y-%m-%d").date(), day["contributionCount"])
                for week in contributions
                for day in week["contributionDays"]
            ],
            columns=["Date", "Commits"]
        )

        st.subheader("Recent Commits")
        st.write(commit_data)

        st.subheader("Commit History Chart")
        st.line_chart(commit_data.set_index("Date")["Commits"])
        
    except Exception as e:
        st.error(f"Error occurred while fetching commit history: {e}")

@handle_errors
def get_pull_requests(token, name):
    """Visualize pull request activity"""
    headers = {"Authorization": f"Bearer {token}"}

    query = """
    {
        user(login: "%s") {
            contributionsCollection {
                pullRequestContributionsByRepository {
                    contributions {
                        totalCount
                    }
                    repository {
                        name
                    }
                }
            }
        }
    }
    """ % name

    try:
        response = requests.post(API_ENDPOINT, json={"query": query}, headers=headers)
        response.raise_for_status()
        data = response.json()
        contributions = data["data"]["user"]["contributionsCollection"]["pullRequestContributionsByRepository"]

        repository_names = [contribution["repository"]["name"] for contribution in contributions]
        pull_request_counts = [contribution["contributions"]["totalCount"] for contribution in contributions]

        df = pd.DataFrame({"Repository": repository_names, "Pull Requests": pull_request_counts})

        st.subheader("Pull Requests Over Time")
        fig = px.bar(df, x="Repository", y="Pull Requests", title="Pull Requests Over Time")
        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Error occurred while fetching pull request data: {e}")

@handle_errors
def get_most_active_day(token, name):
    """Show weekly activity patterns"""
    api_end_point = f"{API_ENDPOINT}/users/{name}/events"
    headers = {"Authorization": f"Token {token}"}

    try:
        response = requests.get(api_end_point, headers=headers)
        response.raise_for_status()
        events = response.json()

        day_counter = Counter()
        for event in events:
            day = pd.Timestamp(event["created_at"]).day_name()
            day_counter[day] += 1

        most_active_days = day_counter.most_common()
        if most_active_days:
            st.subheader("Most Active Days")

            df_days = pd.DataFrame(most_active_days, columns=["Day", "Commits/Pushes"])

            st.line_chart(df_days.set_index("Day"))
        else:
            st.info("No commit/push activity found.")
    except Exception as e:
        st.error(f"Error occurred while fetching most active days: {e}")

# UI and button logic
def main():
    st.set_page_config(
        page_title="GitHub Stats",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="auto",
    )

    st.markdown("<h2 style='text-align: center; color: white;'>Let's get to know your GitHub stats!</h2><br><br>", unsafe_allow_html=True)

    st.sidebar.subheader("GitHub Credentials")
    githubName = st.sidebar.text_input("Enter your GitHub username", help="Enter your GitHub username to fetch your stats")
    token = st.sidebar.text_input("Enter your GitHub personal access token", help="Generate a personal access token in your GitHub settings and enter it here.", type="password")
    num_days = st.sidebar.slider("Select the number of days for commit history", 1, 365, 125)
    st.title("GitHub Repository Stats")

    headers = {"Authorization": f"Bearer {token}"}

    query = """
    {
        user(login: "%s") {
            repositories(first: 100) {
                nodes {
                    name
                }
            }
        }
    }
    """ % githubName

    try:
        response = requests.post(API_ENDPOINT, json={"query": query}, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        repo_nodes = data["data"]["user"]["repositories"]["nodes"]
        repo_names = [repo["name"] for repo in repo_nodes]

        selected_repo = st.sidebar.selectbox('Please choose a repository', options=repo_names, key='project_stats_selectbox')

    except Exception as e:
        st.error(f"Error occurred while fetching repositories: {e}")
        

    btn = st.button("Get your token from github developer settings 😎(opens in a new tab)")
    st.markdown("<p>Click on the new token button, generate a new token with all the permissions for the repo granted, and copy and paste it here, PLEASE!!</p>", unsafe_allow_html=True)

    if btn:
        url_feedback = "https://github.com/settings/tokens?type=beta"
        webbrowser.open(url_feedback)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)


    if col1.button("Show My Stats"):
        if githubName and token:
            get_user_info(token, githubName)
            get_most_used_languages(token, githubName)
        else:
            st.error("Please enter your GitHub username and token in the sidebar.")

    if col2.button("Show Recent Commits"):
        if githubName and token:
            fetch_commit_history(token, githubName, num_days)
        else:
            st.error("Please enter your GitHub username and token in the sidebar.")

    if col3.button("Show Additional Stats"):
        if githubName and token:
            get_pull_requests(token, githubName)
            get_most_active_day(token, githubName)
        else:
            st.error("Please enter your GitHub username and token in the sidebar.")

    if col4.button("Show My Project Stats"):
        if githubName and token:
            
            show_commit_history(selected_repo, githubName, token)
        else:
            st.error("Please enter your GitHub username and token in the sidebar.")
            
            
        
def get_csv_download_link(df):
    """Generate download link for DataFrame"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="commit_history.csv">Download CSV</a>'
    return href
    
def show_commit_history(selected_repo, name, token):
    """Display commit history for a repository"""
    if selected_repo:
        st.subheader(f"Stats are here, boss for : {selected_repo}")

        commit_data = fetch_custom_commit_history(selected_repo, name, token)
        if commit_data is not None:
            st.subheader(f'Commit History for {selected_repo}')

            
            commit_df = pd.DataFrame(commit_data)
            st.write(commit_df)

            
            fig = px.line(commit_df, x="Date", y="Commit Count", title="Commit History")
            st.plotly_chart(fig)

            
            st.markdown(get_csv_download_link(commit_df), unsafe_allow_html=True)



if __name__ == "__main__":
    main()