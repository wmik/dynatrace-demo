import math
from uuid import uuid1
import pandas as pd

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
