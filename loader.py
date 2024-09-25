from components import Team, Talent, Project

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
