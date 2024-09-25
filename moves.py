from components import Project, Talent, Team
from uuid import uuid1
import math
import copy
import streamlit as st
from loader import format_currency

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


def integrate(team):
    moves = []
    info = []
    for talent in team.members:
        for project in talent.projects:
            if project.stage == "Activation" and project.project_status != "initialised":
                if (talent.utilisation + stage_pawn_size[team.team_name]["integration"] / 24) < 1.5:
                    if project.pawns_to_progress == project.current_pawns:
                        project.stage = "Integration"
                        project.current_pawns = talent.stage_pawn_size[talent.talent_seniority]["integration"]
                        project.project_status = "hidden pawns"
                        project.update()
                        talent.idle_pawns += project.pawns_to_progress
                        talent.projects_in_integration += 1
                        talent.projects_in_activation -= 1
                        moves.append(f"Project {project.id} has completed activation")
                    else:
                        if talent.idle_pawns >= project.variance:
                            talent.idle_pawns -= project.variance
                            project.current_pawns += project.variance
                            project.update()
                            moves.append(f"Project {project.id} has completed activation")
                        elif ((talent.idle_pawns + 3) >= project.variance) or ((talent.idle_pawns + 2) >= project.variance) or ((talent.idle_pawns + 1) >= project.variance):
                            talent.bank -= talent.bank - (project.variance - talent.idle_pawns)
                            talent.idle_pawns = 0
                            project.current_pawns += project.variance
                            project.update()
                            moves.append(f"Project {project.id} has completed activation")
                        else:
                            info.append(f"No one was available to activate project {project.id} and prepare it for integration. The team will get a penalty every quarter until they solve the situation.")
                else:
                    info.append(f"No one was available to activate project {project.id} and prepare it for integration. The team will get a penalty every quarter until they solve the situation.")                  
        talent.update()
    team.update()
    return team, moves, info


def optimise(team,pawns_to_integrate):
    moves = []
    info = []
    for talent in team.members:
        for project in talent.projects:
            if project.stage == "Integration":
                if (project.project_status == "hidden pawns") or (project.project_status == "loaded"):
                    project.pawns_to_progress = pawns_to_integrate
                    project.pawns_to_integrate = pawns_to_integrate
                    project.project_status = "resources known"
                    project.update()
                    if project.variance <=0:
                        project.stage = "Integration"
                        moves.append(f"Project {project.id} has completed integration")
                    else:
                        if talent.idle_pawns >= project.variance:
                            talent.total_pawns_to_integrate += pawns_to_integrate
                            talent.idle_pawns -= project.variance
                            project.current_pawns += project.variance
                            project.update()
                            moves.append(f"Project {project.id} has completed integration")
                        else:
                            moves.append(f"Not enough pawns to integrate project {project.id}") 
                elif project.project_status == "resources known":
                    if project.variance <=0:
                        project.stage = "Integrated"
                        project.project_status = "optimised"
                        moves.append(f"Project {project.id} has completed integration")
                    else:
                        if talent.idle_pawns >= project.variance:
                            talent.total_pawns_to_integrate += pawns_to_integrate
                            talent.idle_pawns -= project.variance
                            project.current_pawns += project.variance
                            project.project_status = "optimised"
                            project.update()
                            moves.append(f"Project {project.id} has completed integration")
                        elif ((talent.idle_pawns + 3) >= project.variance) or ((talent.idle_pawns + 2) >= project.variance) or ((talent.idle_pawns + 1) >= project.variance):
                            talent.total_pawns_to_integrate += pawns_to_integrate
                            talent.bank -= talent.bank - (project.variance - talent.idle_pawns)
                            talent.idle_pawns = 0
                            project.current_pawns += project.variance
                            project.project_status = "optimised"
                            project.update()
                            moves.append(f"Project {project.id} has completed integration")

                        else:
                            info.append(f"Not enough pawns to integrate project {project.id}")
        talent.update()
    team.update()
    return team, moves, info


def cruise(team):
    moves = []
    info  = []
    for talent in team.members:
        for project in talent.projects:
            if (project.stage == "Integration"):
                if (project.project_status == "optimised")  or (project.project_status == "loaded"):
                    if project.variance < talent.idle_pawns:
                        project.stage = "Cruise"
                        talent.projects_in_integration -= 1
                        talent.projects_in_cruise +=1
                        talent.total_pawns_to_integrate -= project.pawns_to_integrate
                        moves.append(f"Project {project.id} has completed optimisation. {talent.talent_name} is getting {round(project.current_pawns - talent.stage_pawn_size[talent.talent_seniority]['cruise'])} pawns to work on other things.")
                    else:
                        if talent.bank >0:
                            if ((talent.idle_pawns + 3) >= project.variance) or ((talent.idle_pawns + 2) >= project.variance) or ((talent.idle_pawns + 1) >= project.variance):
                                project.stage = "Cruise"
                                talent.projects_in_integration -= 1
                                talent.projects_in_cruise +=1
                                moves.append(f"Project {project.id} has completed optimisation. {talent.talent_name} is getting {round(project.current_pawns - talent.stage_pawn_size[talent.talent_seniority]['cruise'])} pawns to work on other things.")
                            else:
                                info.append(f"Not enough pawns to optimise project {project.id}")
                        else:
                            info.append(f"Not enough pawns to optimise project {project.id}")
        talent.update()
    team.update()
    return team,moves,info
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
def check_projects(team,pawns_to_integrate):
    activations = []
    inits = []
    for i,talent in enumerate(team.members):
        if talent.idle_pawns >= stage_pawn_size[team.team_name]["activation"]:
            talent.projects.append(
                Project(p_id = uuid1(),
                        talent_name=talent.talent_name,\
                        talent_seniority=talent.talent_seniority,\
                        project_start = None,\
                        pawns_to_integrate = stage_pawn_size[talent.talent_seniority]["integration"],\
                        revenues=0,\
                        stage = "Activation",\
                        project_status = "activated",\
                        pawns_to_progress = stage_pawn_size[talent.talent_seniority]["activation"],\
                        current_pawns = stage_pawn_size[talent.talent_seniority]["activation"]\
                )
            )
            talent.projects_in_activation += 1
            talent.update()
            activations.append(i)
        elif talent.bank > 0:
            if ((talent.idle_pawns + 3) >= stage_pawn_size[team.team_name]["activation"]) or ((talent.idle_pawns + 2) >= stage_pawn_size[team.team_name]["activation"]) or ((talent.idle_pawns + 1) >= stage_pawn_size[team.team_name]["activation"]):
                talent.projects.append(
                    Project(p_id = uuid1(),
                            talent_name=talent.talent_name,\
                            talent_seniority=talent.talent_seniority,\
                            project_start = None,\
                            pawns_to_integrate = stage_pawn_size[talent.talent_seniority]["integration"],\
                            revenues=0,\
                            stage = "Activation",\
                            project_status = "activated",\
                            pawns_to_progress = stage_pawn_size[talent.talent_seniority]["activation"],\
                            current_pawns = stage_pawn_size[talent.talent_seniority]["activation"]\
                    )
                )
                talent.projects_in_activation += 1
                talent.update(),
                activations.append(i)
            elif ((talent.idle_pawns + 3) >= status_pawn_size[team.team_name]["initialised"]) or ((talent.idle_pawns + 2) >= stage_pawn_size[team.team_name]["initialised"]) or ((talent.idle_pawns + 1) >= stage_pawn_size[team.team_name]["initialised"]):
                talent.projects.append(
                    Project(p_id = uuid1(),
                            talent_name=talent.talent_name,\
                            talent_seniority=talent.talent_seniority,\
                            project_start = None,\
                            pawns_to_integrate = stage_pawn_size[talent.talent_seniority]["integration"],\
                            revenues=0,\
                            stage = "Activation",\
                            project_status = "initialised",\
                            pawns_to_progress = stage_pawn_size[talent.talent_seniority]["activation"],\
                            current_pawns = status_pawn_size[talent.talent_seniority]["initialised"]\
                    )
                )
                talent.pawns_in_initialisation += status_pawn_size[talent.talent_seniority]["initialised"]
                talent.update()
                inits.append(i)
            else:
                #print(f"project cannot be activated or initialised for {talent.talent_name}")
                pass
        else:
            #print(f"project cannot be activated or initialised for {talent.talent_name}")
            pass

    team,c_moves ,info= cruise(team)
    team,o_moves ,info= optimise(team,pawns_to_integrate)
    team,i_moves ,info = integrate(team)
    #team,c_moves = cruise(team)
    #team,o_moves = optimise(team,8)
    #team,i_moves = integrate(team)

    if len(activations) >0:
        ut = []
        for index in activations:
            ut.append(team.members[index].utilisation)
        if (min(ut) + stage_pawn_size[team.team_name]["activation"] / 24) < 1.5:
            t_index = activations[ut.index(min(ut))]
        else:
            t_index = math.nan
    else:
        if len(inits) >0:
            ut = []
            for index in inits:
                ut.append(team.members[index].utilisation)
                if (min(ut) + status_pawn_size[team.team_name]["initialised"] / 24) < 1.5:
                    t_index = inits[ut.index(min(ut))]
                else:
                    t_index = math.nan
        else:
            t_index = math.nan
    return t_index


def insert_project(t_index,team):
    talent = team.members[t_index]
    if talent.idle_pawns >= stage_pawn_size[team.team_name]["activation"]:
        talent.projects.append(
            Project(p_id = uuid1(),
                    talent_name=talent.talent_name,\
                    talent_seniority=talent.talent_seniority,\
                    project_start = None,\
                    pawns_to_integrate = stage_pawn_size[talent.talent_seniority]["integration"],\
                    revenues=0,\
                    stage = "Activation",\
                    project_status = "activated",\
                    pawns_to_progress = stage_pawn_size[talent.talent_seniority]["activation"],\
                    current_pawns = stage_pawn_size[talent.talent_seniority]["activation"]\
            )
        )
        talent.projects_in_activation += 1
        talent.update()
        team.update()
    elif (talent.bank > 0):
        if ((talent.idle_pawns + 3) >= stage_pawn_size[team.team_name]["activation"]) or ((talent.idle_pawns + 2) >= stage_pawn_size[team.team_name]["activation"]) or ((talent.idle_pawns + 1) >= stage_pawn_size[team.team_name]["activation"]):
            talent.projects.append(Project(p_id = uuid1(),
                        talent_name=talent.talent_name,\
                        talent_seniority=talent.talent_seniority,\
                        project_start = None,\
                        pawns_to_integrate = stage_pawn_size[talent.talent_seniority]["integration"],\
                        revenues=0,\
                        stage = "Activation",\
                        project_status = "activated",\
                        pawns_to_progress = stage_pawn_size[talent.talent_seniority]["activation"],\
                        current_pawns = stage_pawn_size[talent.talent_seniority]["activation"]\
                )
            )
            talent.projects_in_activation += 1
            talent.update()
            team.update()
        elif ((talent.idle_pawns + 3) >= status_pawn_size[team.team_name]["initialised"]) or ((talent.idle_pawns + 2) >= stage_pawn_size[team.team_name]["initialised"]) or ((talent.idle_pawns + 1) >= stage_pawn_size[team.team_name]["initialised"]):
            talent.projects.append(
                Project(p_id = uuid1(),
                        talent_name=talent.talent_name,\
                        talent_seniority=talent.talent_seniority,\
                        project_start = None,\
                        pawns_to_integrate = stage_pawn_size[talent.talent_seniority]["integration"],\
                        revenues=0,\
                        stage = "Activation",\
                        project_status = "initialised",\
                        pawns_to_progress = stage_pawn_size[talent.talent_seniority]["activation"],\
                        current_pawns = status_pawn_size[talent.talent_seniority]["initialised"]\
                )
            )
            talent.projects_in_activation += 1
            talent.update()
            team.update()
        else:
            #print(f"project cannot be activated or initialised for {talent.talent_name}")
            pass
    else:
        #print(f"project cannot be activated or initialised for {talent.talent_name}")
        pass
    return team

def calculate_metrics(team,projects,quarters, backlog):
    projects_value = (project_value[team.team_name] * projects) / quarters
    total_salary = (talent_salary[team.team_name]*len(team.members)) / quarters
    utilisation_fine = round(sum([(x.utilisation* talent_salary[team.team_name]) / quarters for x in team.members if x.utilisation >1 ]))
    fine = (len([x for x in team.projects if x.project_status == "initialised"]) * 2500) + (backlog * 5000)
    return projects_value - (total_salary + utilisation_fine + fine)
        



def turn(main_team,prjs,q,pawns_to_integrate,teams):
    main_team,c_moves ,info= cruise(main_team)
    main_team,o_moves ,info= optimise(main_team,pawns_to_integrate)
    main_team,i_moves ,info = integrate(main_team)
    c_moves = "\n".join([f'''<li>{move}</li>''' for move in c_moves])
    o_moves = "\n".join([f'''<li>{move}</li>''' for move in o_moves])
    i_moves = "\n".join([f'''<li>{move}</li>''' for move in i_moves])

    main_team,h_info = handover(main_team)
    h_info_out = "\n".join([f'''<li>{info}</li>''' for info in h_info]) 

    recommendations = []
    projects = 0
    backlog = 0
    for prj in range(prjs):
        team=copy.deepcopy(main_team)                       
        t_index = check_projects(team,pawns_to_integrate)
        if type(t_index) == float:
            # print (f"Could not activate or initialise project {prj}")
            backlog += 1
        else:
            overtime_text = '' if- main_team.members[t_index].active_pawns < 24 else ', although it means working overtime'
            recommendations.append(f"{main_team.members[t_index].talent_name} has enough resources available, and was chosen to activate project {prj+1}{overtime_text}")
            main_team = insert_project(t_index,main_team)
            #print(main_team.members[t_index].talent_name)
    talent_name = ""
    p_moves = []
    if main_team.summary["Utilisation"].mean() >= 1.5:
        teamA = ""
        if main_team.team_name == "P":
            teamA = teams["S"]
        elif main_team.team_name == "S":
            teamA = teams["J"]
        else:
            pass
        if (teamA != "") and (teamA.summary["Utilisation"].min() < 1.2):
            teamA, main_team,talent_name = promote(teamA= teamA, teamB= main_team)
            p_moves.append(f'''Promote {talent_name} to team {team.team_name} but {talent_name} has to wait a turn before they can be assigned projects''')

    margin = round(main_team.total_margin_per_active_pawn)
    recs = "\n".join([f'''<li>{rec}</li>''' for rec in recommendations])
    data = { 'assign': recs, 'integration': i_moves, 'optimisation': o_moves, 'cruise': c_moves, 'handover': h_info_out, 'promotions': p_moves,'summary': main_team.summary, 'margin_per_active_pawn': margin }
    return main_team, backlog, margin, data





def handover(team):
    info = []
    if (max([x.utilisation for x in team.members]) >= 1.5) and (min([x.utilisation for x in team.members]) < .5):
        t1_index = [x.utilisation for x in team.members].index(max([x.utilisation for x in team.members]))
        t2_index = [x.utilisation for x in team.members].index(min([x.utilisation for x in team.members]))
        talent1 = team.members[t1_index]
        talent2 = team.members[t2_index]
        for i,project in enumerate(talent1.projects):
            if project.variance <= talent2.idle_pawns:
                if project.project_status != "signed_off":
                    talent2.projects.append(project)
                    talent1.projects.pop(i)
                    if project.stage == "Activation":
                        talent2.projects_in_activation += 1
                        talent1.projects_in_activation -= 1
                    elif project.stage == "Integration":
                        talent2.projects_in_integration +=1
                        talent2.total_pawns_to_integrate -= project.pawns_to_integrate
                        talent1.projects_in_integration -= 1
                    elif project.stage == "Cruise":
                        talent2.projects_in_cruise +=1
                        talent1.projects_in_cruise -= 1
                    info.append(f"Handed over project {project.id} from {talent1.talent_name} to {talent2.talent_name}")
                    talent2.update()
                    talent1.update()
                    break
        team.update()    
    return team,info



def promote(teamA,teamB):
    rank_index = [x.talent_rank for x in teamA.members].index(min([x.talent_rank for x in teamA.members]))
    talent = teamA.members[rank_index]
    for i,project in enumerate(talent.projects):
        talent_index = [x.active_pawns for x in teamA.members].index(min([x.active_pawns for x in teamA.members]))
        talent2= teamA.members[talent_index]
        if project.current_pawns <= talent2.idle_pawns:
            if project.project_status != "signed_off":
                talent2.projects.append(project)
                talent.projects.pop(i)
                if project.stage == "Activation":
                    talent2.projects_in_activation += 1
                    talent.projects_in_activation -= 1
                elif project.stage == "Integration":
                    talent2.projects_in_integration += 1
                    talent.projects_in_integration -= 1
                elif project.stage == "Cruise":
                    talent2.projects_in_cruise += 1
                    talent.projects_in_cruise -=1 
                talent.update()
                talent2.update()
    teamB.members.append(talent)
    teamA.members.remove(talent)
    talent.projects_in_activation, talent.projects_in_integration,talent.total_pawns_to_integrate, talent.projects_in_cruise = [0,0,0,0]
    talent.talent_seniority = teamB.team_name
    talent.talent_rank = max([x.talent_rank for x in teamB.members]) + 1
    talent.projects = []
    talent.update()
    teamA.update()
    teamB.update()
    return teamA, teamB,talent.talent_name

