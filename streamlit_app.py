import pandas as pd
from uuid import uuid1
import math
import numpy as np
import copy
import random
import math
import streamlit as st
import streamlit.components.v1 as components

from components import Talent, Team, Project
from loader import get_talent_objects, project_data_descriptor,format_currency
from moves import integrate, optimise, promote, cruise, turn ,handover

@st.cache_data
def load_data(filename):
    df=pd.read_csv(filename)
    df = df.fillna(0)
    df["Project ID"] = [int(x) for x in df["Project ID"]]
    return df


def is_int(n):
    try:
        int(n)
        return True
    except:
        return False
        
df=load_data("data2.csv")
st.title("Brave #Fantasy Workforce - Dynatrace")

bank = st.sidebar.slider(
    'Set # of pawns in the bank)',
    0,24,12
)
bank_cap = 3
st.sidebar.subheader('Data display options')
show_company_stats = st.sidebar.checkbox('Show company stats')
show_talent_stats = st.sidebar.checkbox('Show talent stats for Q0')
show_recommendations = st.sidebar.checkbox('Show recommendations', True)
st.sidebar.subheader('Q1')
large_q1 = st.sidebar.slider(
    'Set  # of large projects in Quarter 1',
    1,3,6
)
medium_q1 = st.sidebar.slider(
    'Set  # of medium projects in Quarter 1',
    1,3,6
)
small_q1 = st.sidebar.slider(
    'Set  # of small projects in Quarter 1',
    1,3,6
)
st.sidebar.subheader('Q2')
large_q2 = st.sidebar.slider(
    'Set  # of large projects in Quarter 2',
    1,3,6
)
medium_q2 = st.sidebar.slider(
    'Set  # of medium projects in Quarter 2',
    1,3,6
)
small_q2 = st.sidebar.slider(
    'Set  # of small projects in Quarter 2',
    1,3,6
)
st.sidebar.subheader('Q3')
large_q3 = st.sidebar.slider(
    'Set  # of large projects in Quarter 3',
    1,3,6
)
medium_q3 = st.sidebar.slider(
    'Set  # of medium projects in Quarter 3',
    1,3,6
)
small_q3 = st.sidebar.slider(
    'Set  # of small projects in Quarter 3',
    1,3,6
)
st.sidebar.subheader('Q4')
large_q4 = st.sidebar.slider(
    'Set  # of large projects in Quarter 4',
    1,3,6
)
medium_q4 = st.sidebar.slider(
    'Set  # of medium projects in Quarter 4',
    1,3,6
)
small_q4 = st.sidebar.slider(
    'Set  # of small projects in Quarter 4',
    1,3,6
)
# simulate = st.sidebar.button('Get recommendations')

status_pawn_size = {
    "J":{
        "initialised":1,
    },
    "S":{
        "initialised":1,
    },
    "P":{
        "initialised":3,
    }
}
stage_pawn_size = {
    "J":{
        "activation":2,
        "integration":2,
        "cruise":1,
    },
    "S":{
        "activation":3,
        "integration":3,
        "cruise":2,
    },
    "P":{
        "activation":8,
        "integration":8,
        "cruise":6,
    }
}
project_value = {
    "J":50000,
    "S":150000,
    "P":500000
}

talent_salary = {
    "J":108000,
    "S":134000,
    "P":149000    
}

# st.write("## Current state of the employees.")







talent_list = get_talent_objects(df,bank)
##sorting talent to teams
teams = dict()
for t_name in ["S","J","P"]:
    m_team = []
    for talent in talent_list:
        if talent.talent_seniority == t_name:
            m_team.append(talent)
    team = Team(m_team)
    teams.update({
        t_name:team
    })
# st.write("## Merged caculated pawn data")
pawn_df = pd.DataFrame([{"Person":x.talent_name,"Team":x.talent_seniority} for x in talent_list])
df1 = pd.concat([pawn_df, pd.DataFrame([x.summary for x in talent_list])],axis=1)

# st.write("## Calculating Pawn Data..")





## 5 junior projects, 3 senior projects , 2 Principal projects
### Simulation begin



#talent.stuck_idle_pawns + 

# st.write(f"## Recommendations for {team_name}")
# team=copy.deepcopy(teams)[team_name]

def calculate_metrics(team,projects,quarters, backlog):
    projects_value = (project_value[team.team_name] * projects) / quarters
    total_salary = talent_salary[team.team_name] / quarters
    utilisation_fine = round(sum([(x.utilisation* talent_salary[team.team_name]) / quarters for x in team.members if x.utilisation >1 ]))
    fine = (len([x for x in team.projects if x.project_status == "initialised"]) * 2500) + (backlog * 5000)
    return projects_value - (total_salary + utilisation_fine + fine)
        
# quarters = [q1,q2,q3,q4]


profit_margins = {}

team_name_map = {
    'P': 'Principal team',
    'S': 'Senior team',
    'J': 'Junior team'
}

results = {
    'P': {},
    'S': {},
    'J': {}
}

settings = {
    'P': [large_q1,large_q2,large_q3,large_q4],
    'S': [medium_q1,medium_q2,medium_q3,medium_q4],
    'J': [small_q1,small_q2,small_q3,small_q4]
}

@st.cache_data
def simulation():
    simulation_results = {
        'P': {},
        'S': {}, 
        'J': {}
    }
    for team in simulation_results:
        m_team = copy.deepcopy(teams)[team]
        quarters = settings[team]
        val = stage_pawn_size[team]['integration']
        pawns_to_integrate = random.choice(range(val, (val*2)+1))
        annual_margin = 0
        for i,q in enumerate(quarters):
            m_team,backlog,margin, data = turn(m_team,q,i,pawns_to_integrate,teams)
            simulation_results[team][f'{i + 1}'] = data
            team_margin =  round(calculate_metrics(m_team,settings[team][i],4,backlog)) 
            simulation_results[team][f'{i + 1}']['team_margin'] = team_margin
            annual_margin += team_margin
        projects = sum(quarters) - backlog     
        profit_margins[team] = annual_margin
    return simulation_results

# if simulate:
results= simulation()

principal_team_props = {
    'name': 'Principal team',
    'members': len(df[df['Talent seniority'] == 'P']['Talent'].unique()),
    'project_count': len(df[df['Talent seniority'] == 'P'])
}

senior_team_props = {
    'name': 'Senior team',
    'members': len(df[df['Talent seniority'] == 'S']['Talent'].unique()),
    'project_count': len(df[df['Talent seniority'] == 'S'])
}

junior_team_props = {
    'name': 'Junior team',
    'members': len(df[df['Talent seniority'] == 'J']['Talent'].unique()),
    'project_count': len(df[df['Talent seniority'] == 'J'])
}

def render_card(props):
    return f"""
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">{props['title']}</h5>
                <p class="card-text">{props['text']}</p>
            </div>
        </div>
    """

def render_team_stats(props):
    return f"""
        <h4 style="margin-top: 40px; margin-bottom: 20px;">{props['name']}</h4>
        <div class="card-deck">
            {render_card({ 'title': 'Team members', 'text': props['members'] })}
            {render_card({ 'title': 'Project count', 'text': props['project_count'] })}
            {render_card({ 'title': 'Overtime cap', 'text': f'{bank} pawns' })}
        </div>
    """

team_profit_margins = {
    'Principal team': profit_margins.get('P', 0),
    'Senior team': profit_margins.get('S', 0),
    'Junior team': profit_margins.get('J', 0),
}

def render_profit_margins(props):
    for team_name, profit_margin in props.items():
        st.write(f"""{team_name} - <span style="color:{'limegreen' if profit_margin > 0 else 'crimson'};">{format_currency(round(profit_margin)) if is_int(profit_margin) else '_' }</span>""", unsafe_allow_html=True)

if show_company_stats:
    st.header('Company stats')
    st.subheader('Projected profit margins - end of Q4')
    render_profit_margins(team_profit_margins)

components.html(f"""
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
<table class="table" style="margin-top: 32px;">
    <thead>
        <tr>
            <th>Fines</th>
            <th>$xxxx</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Project in backlog</td>
            <td>$5,000/quarter</td>
        </tr>
        <tr>
            <td>Delayed integration</td>
            <td>$2,500/quarter</td>
        </tr>
    </tbody>
</table>
<div style="display: {"block" if show_company_stats else "none"};">
    <h2 style="margin-top: 40px;">Team stats</h2>
    {render_team_stats(principal_team_props)}
    {render_team_stats(senior_team_props)}
    {render_team_stats(junior_team_props)}
</div>
""",
height=900 if show_company_stats else 0)

if show_talent_stats:
    st.header("Talent stats for Q0")
    df1


if show_recommendations:
    st.write(f"## Recommendations")
    st.write("""
        We have simulated all the different decisions you could make about your team in the next 4 quarters (based on its initial situation in Q0 and the number of projects coming into the sales pipeline) - who should work on what, how much effort that could require, what handovers should take place, who should take on new projects, when to promote talents, etc.
    """)
    st.write("""
        We have picked the scenario that will generate the best margins for your company over a year - these are the decisions we recommend you make.
    """)
    for team_key, team_result in results.items():
        annual_margin = 0
        st.write(f'### {team_name_map[team_key]} recommendations')
        for key, q in team_result.items():
            annual_margin += q['team_margin']
            if is_int(key):
                st.write(f'### Quarter {key} moves')
                if len(q['promotions']) >= 1:
                    st.write(f"""
                        <h4>Promotions this Quarter</h4>
                        <ul style="margin: 20px 0;">
                            {''.join(q['promotions'])}
                        </ul>     
                    """, unsafe_allow_html=True)
                if len(q['handover']) > 0:
                    st.write(f"""
                        <h4>Recommended handover this quarter</h4>
                        <ul style="margin: 20px 0;">
                            {q['handover']}
                        </ul>     
                    """, unsafe_allow_html=True)
                if len(q['assign']) > 0:
                    st.write(f"""
                        <h4>Recommended talent to assign to projects</h4>
                        <ul style="margin: 20px 0;">
                            {q['assign']}
                        </ul>     
                    """, unsafe_allow_html=True)
                st.write(f'''
                    Margin this quarter: <span style="color:{'limegreen;' if q['team_margin'] > 0 else 'crimson;'}">{format_currency(q['team_margin'])}</span>
                ''', unsafe_allow_html=True)
                st.write(f"""
                    <b>Team Stats for Q{key}</b> 
                """, unsafe_allow_html=True)
                st.write(q['summary'])
                
                if len(q['cruise']) > 1:
                    st.write(f"""
                        <h4>Cruise Moves</h4>
                        <ul style="margin: 20px 0;">
                            {q['cruise']}
                        </ul>
                    """, unsafe_allow_html=True)
                if len(q['optimisation']) > 1:
                    st.write(f"""
                        <h4>Optimisation Moves</h4>
                        <ul style="margin: 20px 0;">
                            {q['optimisation']}
                        </ul>
                    """, unsafe_allow_html=True)
                if len(q['integration']) > 1:
                    st.write(f"""
                        <h4>Integration moves</h4>
                        <ul style="margin: 20px 0;">
                            {q['integration']}
                        </ul>
                    """, unsafe_allow_html=True)
                st.write("---")
        
        st.write(f'''## Annual margin for {team_name_map[team_key]} is <span style="color:{'limegreen' if annual_margin > 0 else 'crimson'};">{format_currency(round(annual_margin))}</span>''', unsafe_allow_html=True)
        st.write('---')
