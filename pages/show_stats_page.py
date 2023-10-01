from datetime import datetime, timedelta
import streamlit as st
import requests
from collections import Counter
import pandas as pd
import webbrowser
import json


def fix_json_values(json_to_fix):
    for k, v in json_to_fix.items():
        if str(v) == "False":
            json_to_fix[k] = "No"
        if str(v) == "None":
            json_to_fix[k] = "Not Available"
        if str(v) == "True":
            json_to_fix[k] = "Yes"
    return json_to_fix

def get_most_used_languages(token, name, appendRender=True):
    api_end_point = "https://api.github.com/graphql"
    headers = {"Authorization": "Token " + token}
    query = """
    {
      user (login: "%s") {
        repositories (first: 100) {
          nodes {
            languages (first: 100) {
              nodes {
                name
              }
            }
          }
        }
      }
    }
    """ % name
    try:
        response = requests.post(api_end_point, json={"query": query}, headers=headers)
        response.raise_for_status()
        data = response.json()
        language_counts = Counter()
        for repo in data["data"]["user"]["repositories"]["nodes"]:
            for language in repo["languages"]["nodes"]:
                language_counts[language["name"]] += 1
        most_common_languages = language_counts.most_common(5)
        
        df_languages = pd.DataFrame(most_common_languages, columns=["Language", "Count"])

        if appendRender:
            st.subheader("Most Used Languages")
            st.bar_chart(df_languages.set_index("Language"))
        else:
            lang_list = []
            for lang in most_common_languages:
                lang_list.append(lang[0])
            return lang_list
    except Exception as e:
        st.error(f"Error occurred while fetching languages: {e}")

def get_user_info(token, name):
    base_url = "https://api.github.com"
    api_end_point = f"{base_url}/users/{name}"
    headers = {"Authorization": "Token " + token}

    try:
        response = requests.get(api_end_point, headers=headers)
        response.raise_for_status()
        data = response.json()
        data = fix_json_values(data)
        st.subheader("User Information")
        st.write(f"Developer Name: {data['name']}")
        st.write(f"Contact Email: {data['email']}")
        st.write(f"Number of Public Repositories: {data['public_repos']}")
        st.write(f"Followers: {data['followers']}")
        st.write(f"Following: {data['following']}")
    except Exception as e:
        st.error(f"Error occurred while fetching user information: {e}")

def get_project_stats(token, name):
    st.title("GitHub Repository Stats")


    base_url = "https://api.github.com"
    api_end_point = f"{base_url}/users/{name}/repos"
    headers = {"Authorization": "Token " + token}

    try:
        response = requests.get(api_end_point, headers=headers)
        response.raise_for_status()
        repos = response.json()
        repoNames = [repo['name'] for repo in repos]
        
    
        selected_repo = st.selectbox('Please choose a repository', options=repoNames)

        if selected_repo:
        
            st.subheader(f"Visualization options for {selected_repo}")

        
            show_commits = st.checkbox('Show Commit History')
            if show_commits:
                
                commit_data = fetch_custom_commit_history(selected_repo, name, token)
                if commit_data:
                    
                    st.subheader(f'Commit History for {selected_repo}')
                    st.line_chart(commit_data)
        else:
            st.error("please select a repo")
    except Exception as e:
        st.error(f"Error occurred while fetching repositories: {e}")                                    

def fetch_custom_commit_history(repo_name, username, token):
    base_url = "https://api.github.com"
    api_end_point = f"{base_url}/repos/{username}/{repo_name}/commits"
    headers = {"Authorization": "Token " + token}

    try:
        response = requests.get(api_end_point, headers=headers)
        response.raise_for_status()
        commits = response.json()

    
        commit_data = []
        for commit in commits:
            commit_data.append({
                'Date': commit['commit']['author']['date'],
                'Author': commit['commit']['author']['name'],
                'Message': commit['commit']['message']
            })

    
        df = pd.DataFrame(commit_data)

        return df

    except requests.exceptions.HTTPError as e:
        print(f"Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def fetch_commit_history(token, name, num_days):


    st.title("Your last commits (detailss)")


    base_url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
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
        response = requests.post(base_url, headers=headers, json={"query": query})
        response.raise_for_status()
        data = response.json()

        contributions = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        commit_data = pd.DataFrame(
            [(datetime.strptime(day["date"], "%Y-%m-%d").date(), day["contributionCount"]) for week in contributions for day in week["contributionDays"]],
            columns=["Date", "Commits"]
        )

        st.subheader("Recent Commits")
        st.write(commit_data)

        st.subheader("Commit History Chart")
        st.line_chart(commit_data.set_index("Date")["Commits"])
    except Exception as e:
        st.error(f"Error occurred while fetching commit history: {e}")

def get_pull_requests(token, name):
    base_url = "https://api.github.com"
    api_end_point = f"{base_url}/search/issues?q=author:{name}+type:pr"
    headers = {"Authorization": "Token " + token}

    try:
        response = requests.get(api_end_point, headers=headers)
        response.raise_for_status()
        data = response.json()
        pr_count = data.get("total_count", 0)
        st.subheader("Number of Pull Requests Made")
        st.write(f"{pr_count} pull requests")
    except Exception as e:
        st.error(f"Error occurred while fetching pull request count: {e}")

def get_most_active_day(token, name):
    base_url = "https://api.github.com"
    api_end_point = f"{base_url}/users/{name}/events"
    headers = {"Authorization": "Token " + token}

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

# 404's codes

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

btn = st.button("Get your token from github developer settings 😎(opens in a new tab)")
st.markdown("<p>Click on new token button and generate a new token with all the permissions for the repo granted and copy and paste it here, PLEASE!!</p>",unsafe_allow_html=True)

if btn:
    url_feedback = "https://github.com/settings/tokens?type=beta"
    webbrowser.open(url_feedback)
else: 
    print('testing')    

st.markdown("<br>",unsafe_allow_html=True)    

col1, col2, col3, col4 = st.columns(4)

if col1.button("Show My Stats"):
    if githubName and token:
        get_user_info(token, githubName)
        get_most_used_languages(token, githubName)
    else:
        st.error("Please enter your GitHub username and token in the sidebar.")
if col2.button("Show Recent Commits"):
    if githubName and token:
        fetch_commit_history(token, githubName,num_days)
    else:
        st.error("Please enter your GitHub username and token in the sidebar.")
if col3.button("Show Additional Stats"):
    if githubName and token:
        get_pull_requests(token, githubName)
        get_most_active_day(token, githubName)
    else:
        st.error("Please enter your GitHub username and token in the sidebar.")


if col4.button("show me, my project statssss, pls!"):
    if githubName and token:
        get_project_stats(token, githubName)
    else:
        st.error("Please enter your GitHub username and token in the sidebar.")

