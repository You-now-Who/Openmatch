import streamlit as st
import requests
from collections import Counter
import pandas as pd
import webbrowser
import json

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

        lang_list = []
        for lang in most_common_languages:
            lang_list.append(lang[0])
        return lang_list
    
    except Exception as e:
        # st.error(f"Error occurred while fetching languages: {e}")
        pass

def getOwnerAvatar(owner, token):
      # Try to get avatar of the owner or the organization

      endpoint = 'https://api.github.com/graphql'
      headers = {'Authorization': 'bearer ' + token}

      u_query = f"""{{
        user(login: "{owner}") {{
          avatarUrl
        }}
      }}
      """

      o_query = f"""{{
        organization(login: "{owner}") {{
          avatarUrl
        }}
      }}
      """

      user_response = requests.post(endpoint, json={'query': u_query}, headers=headers)
      org_response = requests.post(endpoint, json={'query': o_query}, headers=headers)

      if user_response.status_code == 200:
        data_u = json.loads(user_response.text)
        try:
          return data_u['data']['user']['avatarUrl']
        except:
          return None
      elif org_response.status_code == 200:
        data_o = json.loads(org_response.text)
        try:
          return data_o['data']['organization']['avatarUrl']
        except:
          return None
      else:
        return None

def get_issues(token, langs, limit=10):
    
    endpoint = 'https://api.github.com/graphql'
    headers = {'Authorization': 'bearer ' + token}
  
    query = """
  {
    search(query: " language:""" + " language:".join(langs) + """", type: ISSUE, first: """ + str(limit) + """) {
      edges {
        node {
          ... on Issue {
            title
            body
            url
            repository {
              name
              owner {
                login
              }
            }
          }
        }
      }
    }
  }
  """
    
    r = requests.post(endpoint, json={'query': query}, headers=headers)

    data = json.loads(r.text)

    issues = data['data']['search']['edges']

    return issues

def get_repos(langs, token, limit=10):

  endpoint = 'https://api.github.com/graphql'
  headers = {'Authorization': 'bearer ' + token}
  
  
  query = """
{
  search(query: "language:""" + " language:".join(langs) + """", type: REPOSITORY, first: """ + str(limit) +""" , orderBy: {field: STARS, direction: DESC}) {
    edges {
      node {
        ... on Repository {
          name
          description
          owner {
            login
          }
          url
        }
      }
    }
  }
}
"""

  r = requests.post(endpoint, json={'query': query}, headers=headers)

  data = json.loads(r.text)
  # return 0
  
  repos = data['data']['search']['edges']

  return repos

def get_open_issues(token, langs, limit=10):
    
    issues = get_issues(token, langs=langs, limit=limit)

    if issues:
        cards_per_row = 3
        num_rows = len(issues) // cards_per_row

        card_style = """
        <style>
        .card {
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            margin: 10px;
            box-shadow: 2px 2px 5px #888888;
        }
        </style>
        """

        # Inject the CSS style into the Streamlit app
        st.markdown(card_style, unsafe_allow_html=True)

        # Remove all the issues that don't have a title
        issues = [issue for issue in issues if issue['node']]

        # Display repositories in cards layout
        for row in range(num_rows):
            columns = st.columns(cards_per_row)
            for i in range(cards_per_row):
                index = row * cards_per_row + i
                if index < len(issues):
                    issue = issues[index]['node']
                    print(issue.keys())
                    with columns[i]:
                        try:
                          st.write(f"**{issue['title']}**")
                          # show only first 100 characters of the body
                          st.write(issue['body'][:100] + '...')
                          st.markdown(f"[GitHub Link]({issue['url']})", unsafe_allow_html=True)
                        except:
                          st.write(f"**UNABLE TO FETCH ISSUE**")


def get_opensource_projects(token, user, langs, limit=10):

    repos = get_repos(langs, token, limit)

    if repos:
        # Define the number of cards per row
        cards_per_row = 3

        # Calculate the number of rows required
        num_rows = len(repos) // cards_per_row

        # Define a CSS class for the card style
        card_style = """
        <style>
        .card {
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            margin: 10px;
            box-shadow: 2px 2px 5px #888888;
        }
        </style>
        """

        # Inject the CSS style into the Streamlit app
        st.markdown(card_style, unsafe_allow_html=True)

        # Display repositories in cards layout
        for row in range(num_rows):
            columns = st.columns(cards_per_row)
            for i in range(cards_per_row):
                index = row * cards_per_row + i
                if index < len(repos):
                    repo = repos[index]['node']
                    owner = repo['owner']

                    avatarUrl = getOwnerAvatar(owner['login'], token)
                    if avatarUrl == None:
                        avatarUrl = 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png'
                    with columns[i]:
                        st.image(avatarUrl, width=100, output_format='PNG')
                        
                        st.write(index+1)
                        st.write(f"**{repo['name']}**")
                        st.write(repo['description'])
                        st.write(f"Author: {repo['owner']['login']}")
                        st.markdown(f"[GitHub Link]({repo['url']})", unsafe_allow_html=True)
                        # st.markdown('</div>', unsafe_allow_html=True)
    pass



st.set_page_config(
    page_title="GitHub Stats",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown("<h2 style='text-align: center; color: white;'>Let's find some open source projects for you to contribute!</h2><br><br>", unsafe_allow_html=True)

st.sidebar.subheader("GitHub Credentials")
githubName = st.sidebar.text_input("Enter your GitHub username", help="Enter your GitHub username to fetch your stats")
token = st.sidebar.text_input("Enter your GitHub personal access token", help="Generate a personal access token in your GitHub settings and enter it here.", type="password")

# btn = st.button("Get your token from github developer settings 😎(opens in a new tab)")
# st.markdown("<p>Click on new token button and generate a new token with all the permissions for the repo granted and copy and paste it here, PLEASE!!</p>",unsafe_allow_html=True)

# if btn:
#     url_feedback = "https://github.com/settings/tokens?type=beta"
#     webbrowser.open(url_feedback)
# else: 
#     print('testing')  

repo_limit = st.slider("Number of repositories to fetch", 0, 50, 9, 3)

try:
    langs = get_most_used_languages(token, githubName)

    options = st.multiselect("Select the languages you want to filter by", langs, default=langs)
    if options:
        langs = options
except:
    langs = []
    st.error("Please enter your GitHub username and token in the sidebar.")

btn_fetch_repos = st.button("Show Repositories")
btn_fetch_issues = st.button("Show Good First Issues")

if btn_fetch_repos and langs:
    if githubName and token:
        get_opensource_projects(token, user=githubName, langs=langs, limit=(repo_limit))
    else:
        st.error("Please enter your GitHub username and token in the sidebar.")

if btn_fetch_issues and langs:
    if githubName and token:
        get_open_issues(token, langs=langs, limit=(repo_limit))
    else:
        st.error("Please enter your GitHub username and token in the sidebar.")

if not githubName or not token:
    st.sidebar.warning("Please enter your GitHub username and token in the sidebar.")