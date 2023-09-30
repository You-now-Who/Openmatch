import streamlit as st
import requests
from collections import Counter
import pandas as pd
import webbrowser

def fix_json_values(json_to_fix):
    for k, v in json_to_fix.items():
        if str(v) == "False":
            json_to_fix[k] = "No"
        if str(v) == "None":
            json_to_fix[k] = "Not Available"
        if str(v) == "True":
            json_to_fix[k] = "Yes"
    return json_to_fix

def get_most_used_languages(token, name):
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
        
    
        st.subheader("Most Used Languages")
        st.bar_chart(df_languages.set_index("Language"))
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

def get_last_commits(token, name):
    base_url = "https://api.github.com"
    api_end_point = f"{base_url}/users/{name}/events"
    headers = {"Authorization": "Token " + token}

    try:
        response = requests.get(api_end_point, headers=headers)
        response.raise_for_status()
        events = response.json()

        push_events = [event for event in events if event["type"] == "PushEvent"]

        if push_events:
            st.subheader("Recent Commits")
            for push_event in push_events[:5]:
                for commit in push_event["payload"]["commits"]:
                    st.write(f"- {commit['message']}")
        else:
            st.info("No recent commits found.")
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

btn = st.button("Get your token from github developer settings 😎(opens in a new tab)")
st.markdown("<p>Click on new token button and generate a new token with all the permissions for the repo granted and copy and paste it here, PLEASE!!</p>",unsafe_allow_html=True)

if btn:
    url_feedback = "https://github.com/settings/tokens?type=beta"
    webbrowser.open(url_feedback)
else: 
    print('testing')    

st.markdown("<br>",unsafe_allow_html=True)    

col1, col2, col3 = st.columns(3)

if col1.button("Show My Stats"):
    if githubName and token:
        get_user_info(token, githubName)
        get_most_used_languages(token, githubName)
    else:
        st.error("Please enter your GitHub username and token in the sidebar.")
if col2.button("Show Recent Commits"):
    if githubName and token:
        get_last_commits(token, githubName)
    else:
        st.error("Please enter your GitHub username and token in the sidebar.")
if col3.button("Show Additional Stats"):
    if githubName and token:
        get_pull_requests(token, githubName)
        get_most_active_day(token, githubName)
    else:
        st.error("Please enter your GitHub username and token in the sidebar.")

