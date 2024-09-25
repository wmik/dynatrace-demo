import pandas as pd
from uuid import uuid1
import math
import numpy as np
import copy
import random
import math
import streamlit as st
import streamlit.components.v1 as components

# components.py
class Project:
    def __init__(self,p_id, talent_name,\
                    talent_seniority,\
                    project_start,\
                    pawns_to_integrate,\
                    revenues,\
                    stage, project_status, pawns_to_progress, current_pawns):
        self.id = p_id
        self.talent_name = talent_name
        self.talent_seniority = talent_seniority
        self.project_start = project_start
        self.pawns_to_integrate = pawns_to_integrate
        self.revenues = revenues
        self.stage = stage
        self.project_status = project_status
        self.pawns_to_progress = pawns_to_progress
        self.current_pawns = current_pawns
        self.pawn_counter()
    def pawn_counter(self):
        self.variance = self.pawns_to_progress - self.current_pawns
    def update(self):
        self.pawn_counter()



class Talent:
    value_per_project = {
        "S":50000,
        "J":150000,
        "P":500000,
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

    cost_per_talent = {
        "S" : 108000,
        "J" : 134000,
        "P" : 149000
    }
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

    def __init__( self,talent_name, talent_seniority,talent_rank, projects_in_cruise, projects_in_activation, projects_in_integration, total_revenue,projects,pawns_in_initialisation = 0, bank = 12, total_pawns = 24):
        self.talent_name = talent_name
        self.talent_rank = talent_rank
        self.total_pawns = total_pawns
        self.pawns_in_initialisation = pawns_in_initialisation
        self.talent_seniority= talent_seniority
        #self.total_revenue = total_revenue
        self.projects_in_cruise = projects_in_cruise
        self.projects_in_activation = projects_in_activation
        self.projects_in_integration = projects_in_integration
        self.bank_val = bank
        self.projects = projects
        self.id = uuid1()
        self.total_pawns_to_integrate = 0

        self.pawn_counter()
        self.revenue_counter()
        self.future_projects_counter()
        self.talent_summary()
    
    def __str__(self):
        return f"Talent Name {self.talent_name}"

    def pawn_counter(self):
        self.total_projects = self.projects_in_cruise + self.projects_in_activation +self.projects_in_integration
        self.pawns_in_activation = (self.projects_in_activation * Talent.stage_pawn_size[self.talent_seniority]["activation"]) + self.pawns_in_initialisation
        if self.projects_in_integration > 0:
            self.pawns_in_integration = (self.projects_in_integration * Talent.stage_pawn_size[self.talent_seniority]["integration"]) + self.total_pawns_to_integrate
        else:
            self.pawns_in_integration = 0
            self.total_pawns_to_integrate = 0
        self.pawns_in_cruise = (self.projects_in_cruise * Talent.stage_pawn_size[self.talent_seniority]["cruise"])
        #self.pawns_in_initialisation = self.projects_in_initialisation * Talent.status_pawn_size[self.talent_seniority]["initialised"]
        self.active_pawns = self.pawns_in_activation + self.pawns_in_integration + self.pawns_in_cruise
        
        if self.projects_in_integration > 0:
            self.pawns_in_integration_per_project = 0#round( self.pawns_in_integration / self.projects_in_integration) ### to be reviewed later
        else:
            self.pawns_in_integration_per_project = 0
        if math.isnan(self.active_pawns):
            self.idle_pawns = self.total_pawns
        else:
            if self.active_pawns <= self.total_pawns:
                self.idle_pawns = self.total_pawns - self.active_pawns
                self.bank = self.bank_val
            else:
                self.bank = self.bank_val -(self.active_pawns - self.total_pawns)
                self.idle_pawns = 0
        self.utilisation = self.active_pawns / self.total_pawns
    
    def revenue_counter(self):
        self.total_revenue_per_pawn = (self.total_projects * Talent.value_per_project[self.talent_seniority]) / self.total_pawns
        if self.active_pawns > 0:
            self.revenue_per_active_pawn = (self.total_projects * Talent.value_per_project[self.talent_seniority]) / self.active_pawns
        else:
            self.revenue_per_active_pawn = 0
        if self.pawns_in_integration > 0:
            self.revenue_per_pawn_in_integration = (self.total_projects * Talent.value_per_project[self.talent_seniority]) / self.pawns_in_integration
        else:
            self.revenue_per_pawn_in_integration = 0
        self.total_cost_per_pawn = self.cost_per_talent[self.talent_seniority] / self.total_pawns
        self.total_margin_per_pawn = self.total_revenue_per_pawn - self.total_cost_per_pawn
        self.margin_per_active_pawn = self.revenue_per_active_pawn - self.total_cost_per_pawn # to be updated
        if self.revenue_per_pawn_in_integration > 0:
            self.margin_per_pawn_in_integration = self.revenue_per_pawn_in_integration - self.total_cost_per_pawn
        else:
            self.margin_per_pawn_in_integration = 0
        
    def future_projects_counter(self):
        if not math.isnan(self.idle_pawns):
            self.new_projects_capacity = math.floor( self.idle_pawns / Talent.stage_pawn_size[self.talent_seniority]["activation"])
            self.stuck_idle_pawns = self.idle_pawns - (self.new_projects_capacity * Talent.stage_pawn_size[self.talent_seniority]["activation"])
        else:
            self.new_projects_capacity = 0
            self.stuck_idle_pawns = 0
    
    def talent_summary(self):
        self.summary={
            "Name":self.talent_name ,
            "Rank":self.talent_rank,
            "Projects in activation":self.projects_in_activation,
            "Projects in integration": self.projects_in_integration,
            "Projects in cruise": self.projects_in_cruise,
            "Pawns in Activation":self.pawns_in_activation,
            "Pawns in integration":self.pawns_in_integration,
            "Pawns to integrate":self.total_pawns_to_integrate,
            "Pawns in cruise":self.pawns_in_cruise,
            "Active pawns":self.active_pawns,
            "Pawns in integration per project":self.pawns_in_integration_per_project,
            "Idle pawns":self.idle_pawns,
            "Bank":self.bank,
            "Utilisation": self.utilisation,
            "New projects capacity": self.new_projects_capacity,
            "Stuck idle pawns": self.stuck_idle_pawns,
            "Total Revenue per pawn":self.total_revenue_per_pawn,
            "Revenue per active pawn":self.revenue_per_active_pawn,
            "Revenue per pawn in integration": self.revenue_per_pawn_in_integration,
            "Total cost per pawn":self.total_cost_per_pawn,
            "Total margin per pawn":self.total_margin_per_pawn,
            "Total margin per active pawn":self.margin_per_active_pawn,
            "Margin per pawn in integration":self.margin_per_pawn_in_integration,

        }
    def update(self):
        self.pawn_counter()
        self.revenue_counter()
        self.future_projects_counter()
        self.talent_summary()

class Team:
    def __init__(self,members):
        self.members = members
        self.total_members = len(members)
        self.team_name = members[0].talent_seniority
        self.calculate_stats()
        self.project_calculator()
        self.team_summary() 
        
    def calculate_stats(self):
        self.projects_in_activation = sum([x.projects_in_activation for x in self.members])
        self.projects_in_integration = sum([x.projects_in_integration for x in self.members])
        self.projects_in_cruise = sum([x.projects_in_cruise for x in self.members])
        self.total_margin_per_active_pawn = sum([x.margin_per_active_pawn for x in self.members])
        self.new_projects_capacity = sum([x.new_projects_capacity for x in self.members])
    def project_calculator(self):
        self.projects = []
        for member in self.members:
            self.projects += member.projects
    def update(self):
        self.calculate_stats()
        self.project_calculator()
        self.team_summary()        
    def team_summary(self):
        self.summary = pd.DataFrame([talent.summary for talent in self.members]).round()

# loader.py
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

def project_data_descriptor(df):
    data = []
    for name in df["Talent"].unique():        
        mdf = df[df["Talent"]==name]
        talent_seniority = mdf["Talent seniority"].values[0]
        talent_rank = mdf["Rank"].values[0]
        metrics = mdf["Project Status"].value_counts().to_dict()
        p_data = mdf.to_dict(orient = "records")
        project_list = []
        for obj in p_data:
            project = Project(
                p_id = obj['Project ID'],\
                talent_name = obj['Talent'],\
                talent_seniority = obj["Talent seniority"],\
                project_start = obj["Project Start"],\
                pawns_to_integrate = stage_pawn_size[talent_seniority]["integration"],\
                revenues = project_value[talent_seniority],\
                stage = obj["Project Status"],\
                project_status = "loaded",\
                pawns_to_progress = obj["Pawns to Progress to next Life Stage"],\
                current_pawns = obj["Pawns Placed Currently"]
            )
            project_list.append(project)
        data.append({
            "talent_name":name,
            "talent_rank":talent_rank,
            "talent_seniority":talent_seniority,
            "metrics":metrics,
            "projects":project_list
        })
    return data



def get_talent_objects(df,bank):
    data = project_data_descriptor(df)
    talent_list = []
    for row in data:
        talent=Talent(
            talent_name = row["talent_name"],
            talent_seniority = row["talent_seniority"],
            talent_rank = row["talent_rank"],
            projects_in_cruise = row["metrics"]["Cruise"] if "Cruise" in row["metrics"] else 0,
            projects_in_activation = row["metrics"]["Activation"] if "Activation" in row["metrics"] else 0,
            projects_in_integration = row["metrics"]["Integration"] if "Integration" in row["metrics"] else 0,
            projects = row["projects"],
            total_revenue = 0,
            bank = bank
        )
        talent_list.append(talent)
    return talent_list


def format_currency(value):
    return "${:,}".format(value)

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
