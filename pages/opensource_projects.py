import streamlit as st
import requests
from collections import Counter
import pandas as pd
import webbrowser
import json

# constants and Configuration
API_ENDPOINT = "https://api.github.com/graphql"
DEFAULT_AVATAR = "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
LICENSES = [
    "Any", "MIT", "GPL-3.0", "GPL-2.0", "Apache-2.0", 
    "BSD-3-Clause", "BSD-2-Clause", "MPL-2.0", 
    "LGPL-3.0", "LGPL-2.1", "EPL-2.0", "CDDL-1.1",
    "ISC", "Unlicense", "AGPL-3.0"
]

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
  
# improved language detection with caching
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_most_used_languages(token, name):
    if not token or not name:
        raise ValueError("Missing required credentials")
        
    query = """
    {
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
    }
    """ % name
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(API_ENDPOINT, json={"query": query}, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    language_counts = Counter()
    
    for repo in data["data"]["user"]["repositories"]["nodes"]:
        for language in repo["languages"]["nodes"]:
            language_counts[language["name"]] += 1
            
    return [lang[0] for lang in language_counts.most_common(5)]

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

def get_repos(langs, token, filters, limit=10):

  endpoint = 'https://api.github.com/graphql'
  headers = {'Authorization': 'bearer ' + token}
  
  query = ""

  if filters != {}:
      query_string = ""
      available_filters = filters.keys()

      final_filters = []
    
    
      language_filters = " ".join([f'language:{lang}' for lang in langs])
      final_filters.append(language_filters)

      if "topics" in available_filters:
        if filters["topics"] != "":
          topics = filters["topics"].split(",")
          topic_filters = " ".join([f'topic:{topic}' for topic in topics])
          final_filters.append(topic_filters)

      if "min_stars" in available_filters:
        min_stars = filters["min_stars"]
        min_stars_filter = f"stars:>{min_stars}"
        final_filters.append(min_stars_filter)

      if "min_commits" in available_filters:
        min_commits = filters["min_commits"]
        min_commits_filter = f"commits:>{min_commits}"
        final_filters.append(min_commits_filter)

      if "min_issues" in available_filters:
        min_issues = filters["min_issues"]
        min_issues_filter = f"issues:>{min_issues}"
        final_filters.append(min_issues_filter)

      if "date" in available_filters:
        date = filters["date"]
        date_text = filters["date_text"]
        date_filter = f"created:{date_text}{date}"
        final_filters.append(date_filter)

      if "order_by" in available_filters:
        order_by = filters["order_by"]
        order_by_filter = f"sort:{order_by}"
        final_filters.append(order_by_filter)

      for f in final_filters:
        print(f)
        query_string += f + " "

      query = """
          {
            search(query: \" """ + query_string + """ \", type: REPOSITORY, first: """ + str(limit) +""") {
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
      pass

  else:
  
    query = """
  {
    search(query: "language:""" + " language:".join(langs) + """ ", type: REPOSITORY, first: """ + str(limit) +""") {
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
  print(data)

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
                          
#project card
def project_card(repo, index, avatar_url):
    card_html = f"""
    <div style="
        background: #1e1e1e;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    ">
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <img src="{avatar_url}" style="width: 40px; height: 40px; border-radius: 50%; margin-right: 10px;">
            <h3 style="margin: 0; color: #58a6ff;">{repo['name']}</h3>
        </div>
        <p style="color: #8b949e; font-size: 0.9rem;">
            {repo.get('description', 'No description available')[:120]}...
        </p>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="color: #c9d1d9; font-size: 0.8rem;">
                👤 {repo['owner']['login']}
            </span>
            <a href="{repo['url']}" target="_blank" 
               style="color: #58a6ff; text-decoration: none; font-size: 0.8rem;">
                View on GitHub →
            </a>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
#  main function with filters
@handle_errors
def get_opensource_projects(token, user, langs, filters, limit=9):
    if not token or not user:
        raise ValueError("GitHub credentials are required")
    
    # build query with filters
    query_parts = [f"language:{lang}" for lang in langs]
    
    if filters.get("min_stars"):
        query_parts.append(f"stars:>={filters['min_stars']}")
    if filters.get("license") and filters["license"] != "Any":
        query_parts.append(f"license:{filters['license']}")
    
    query = " ".join(query_parts)
    
    gql_query = f"""
    {{
        search(query: "{query}", type: REPOSITORY, first: {limit}) {{
            edges {{
                node {{
                    ... on Repository {{
                        name
                        description
                        stargazerCount
                        url
                        owner {{
                            login
                        }}
                    }}
                }}
            }}
        }}
    }}
    """
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(API_ENDPOINT, json={"query": gql_query}, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    repos = [edge["node"] for edge in data["data"]["search"]["edges"]]
    
    if not repos:
        return st.info("🚨 No projects found matching your criteria")
    
    st.subheader("🔍 Matching Open-Source Projects")
    for i, repo in enumerate(repos, 1):
        avatar_url = getOwnerAvatar(repo["owner"]["login"], token) or DEFAULT_AVATAR
        project_card(
            repo=repo,
            index=i,
            avatar_url=avatar_url
        )

# enhanced UI configuration
st.set_page_config(
    page_title="OpenMatch - Discover Projects",
    page_icon="🔍",
    layout="wide",
)

st.markdown("""
    <h1 style='color: white; text-align: center;'>
        Discover Open-Source Projects
    </h1>
    <p style='text-align: center; color: #8b949e;'>
        Find projects matching your skills and interests
    </p>
""", unsafe_allow_html=True)

# improved Sidebar Filters
with st.sidebar:
    st.header("🔎 Filters")
    token = st.text_input("GitHub Token", type="password")
    username = st.text_input("GitHub Username")
    
    try:
        langs = get_most_used_languages(token, username) if token and username else []
    except:
        langs = []
    
    selected_langs = st.multiselect(
        "Languages", 
        options=langs,
        default=langs,
        help="Select programming languages to filter by"
    )
    
    with st.expander("Advanced Filters"):
        min_stars = st.number_input("Minimum Stars", min_value=0, value=10)
        license_type = st.selectbox("License", LICENSES)
    
    st.markdown("---")
    st.info("💡 Tip: Add more languages to see better matches")



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

repo_limit = st.slider("Number of repositories to fetch", 0, 50, 9, 3)

filters = {}

try:
    langs = get_most_used_languages(token, githubName)

    options = st.multiselect("Select the languages you want to filter by", langs, default=langs)

    if options:
        langs = options

    show_extra_filters = st.checkbox("Show extra filters")

    if show_extra_filters:

      st.subheader("Extra Filters")
      chosen_filters = st.multiselect("Select the filters you want to apply", ["Topics", "Minimum Stars", "Minimum Commits", "Minimum Issues", "Date", "Order By", "License"], default=["Topics", "Minimum Stars", "Minimum Commits", "Minimum Issues", "Date", "Order By", "License"])

      if "Topics" in chosen_filters:
        filters["topics"] = st.text_input("Enter topics to filter by", help="Enter topics separated by commas. For example: hacktoberfest2023, AI, Rust, etc")
      if "Minimum Stars" in chosen_filters:
        filters["min_stars"] = st.number_input("Minimum Stars", min_value=0)
      if "Minimum Commits" in chosen_filters:
        filters["min_commits"] = st.number_input("Minimum Commits", min_value=0)
      if "Minimum Issues" in chosen_filters:
        filters["min_issues"] = st.number_input("Minimum Issues", min_value=0)
      if "Date" in chosen_filters:
        filters["date"] = st.date_input("Date", help="Enter the date after which the repositories were created")
        filters["date_text"] = st.selectbox("Date of creation", ["Before", "After", "On"])
      if "Order By" in chosen_filters:
        filters["order_by"] = st.radio("Order By", ["Stars", "Forks", "Recent"])
      if "License" in chosen_filters:
        filters["project_license"] = st.selectbox("License", licenses)


except Exception as e:
    langs = []
    # st.error(e)
    print(e)
    st.error("Please enter your GitHub username and token in the sidebar.")

btn_fetch_repos = st.button("Show Repositories")
btn_fetch_issues = st.button("Show Good First Issues")

if btn_fetch_repos and langs:
    if githubName and token:
        get_opensource_projects(token, user=githubName, langs=langs, filters=filters, limit=(repo_limit))
    else:
        st.error("Please enter your GitHub username and token in the sidebar.")

if btn_fetch_issues and langs:
    if githubName and token:
        get_open_issues(token, langs=langs, limit=(repo_limit))
    else:
        st.error("Please enter your GitHub username and token in the sidebar.")

if not githubName or not token:
    st.sidebar.warning("Please enter your GitHub username and token in the sidebar.")