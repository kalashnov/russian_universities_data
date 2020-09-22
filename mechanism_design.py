from collections import defaultdict, Counter
import pandas as pd
import numpy as np
import json

class Economy(object):
    def __init__(self, type_space, distribution_function, utilities):
        self.type_space = type_space
        self.distribution_function = distribution_function  # (can be correlated)
        self.utilities = utilities

    # + social_value_function (and some basic -- ex-post/ex-ante)


class BaseMechanism(object):  # or metaclass -- because smth like concrete settings will be needed to be implemented
    def __init__(self, action_space, outcome_func, economy):
        self.action_space
        self.utility_func = utility_func


class AnonimousMechanism(BaseMechanism):
    def __init__(self, n_players, one_action_space, outcome_func, economy):
        self.n_players = n_players
        self.one_action_space = one_action_space
        self.utility_func = utility_func  # validate?
        super().__init__([one_action_space] * n_players, [one_utility_func] * n_players, economy)

    def get_induced_game(self):
        pass  # returns game + bayes nash can draw types + strategy method can be applied + iterative games can be made + ?


class DAMechanism(object): # + visualization
    # tie breaking
    # another interface
    # CASE WHEN 2
    # UNKNOWN?
    # rename action to application
    # BE INTERESTED IN SOCIAL SCIENCE
    # THIS IS ESTECIALLY FOR SCHOOLS, BUT WHAT IF
    def __init__(self, school_capacities, student_capacities):
        # need default values and some tricky things when unknown -- default dict is okay
        self.school_capacities = school_capacities
        self.school_capacities['UNALLOCATED'] = 2**31
        self.student_capacities = student_capacities

    def apply(self, actions, school_preferences): # allocation тоже лучше как объект. И разные представления у него
        # cannot do student things as default dict. Make it possible -- infer and save students n
        # plenty of bugs including
        actions = {k: list(reversed(v)) for k, v in actions.items()}
        allocation = defaultdict(set)
        appliers = Counter(self.student_capacities)

        while sum(appliers.values()) != 0:
            for p, v in appliers.items():
                for _ in range(v):
                    if len(actions[p]) > 0:
                        next_action = actions[p].pop()
                        allocation[next_action].add(p)
                    else:
                        allocation['UNALLOCATED'].add(p) # cannot hold two of them

            new_allocation = defaultdict(set)
            for school, applicants in allocation.items():
                filtered_allocation = set()
                for applicant in school_preferences[school]:
                    if applicant in applicants:
                        filtered_allocation.add(applicant)
                    if len(filtered_allocation) >= self.school_capacities[school]:
                        break
                new_allocation[school] = filtered_allocation
            allocation = new_allocation

            appliers = Counter(self.student_capacities)
            for alloc in allocation.values():
                appliers.subtract(alloc)

        return {k: list(v) for k, v in allocation.items()}

# revelation_function
# move to IC mechanisms from beginning + implementablilty questiins
# + social_choice_function ????


# заботай algorithmic game theory here

# = numerical libraries here

# comparative statics

# mb take a functional manner? -- by what about that cool ML?

if __name__ == '__main__':
    # interface, write formats, to/from pandas formats, ++ ??
    # сделать инструмент!
    rating_data = pd.read_csv('rating.csv')
    rating_data.iloc[rating_data.iloc[:, 1].isna(),1] = 5
    rating_data.iloc[rating_data.iloc[:, 2].isna(),2] = 7
    rating_data.iloc[rating_data.iloc[:, 3].isna(),3] = 2
    rating_data.iloc[rating_data.iloc[:, 4].isna(),4] = 3
    rating_data.iloc[rating_data.iloc[:, 5].isna(),5] = 4
    rating_data.iloc[rating_data.iloc[:, 6].isna(),6] = 6
    rating_data.iloc[rating_data.iloc[:, 7].isna(),7] = 1
    student_capacities = dict(zip(rating_data['fio'], np.repeat(2, len(rating_data['fio']))))
    mech = DAMechanism(school_capacities=defaultdict(lambda: 50), student_capacities=student_capacities)
    school_preferences = defaultdict(lambda: list(rating_data['fio']))
    actions = dict()
    for i, row in rating_data.iterrows():
        student = row['fio']
        schools = row.iloc[1:]
        actions[student] = sorted(schools.index.values, key=lambda x: schools[x])

    alloc = mech.apply(actions, school_preferences)

    json.dump(alloc, open('alloc.json', 'w'), indent=4, ensure_ascii=False)

    alloc.items()

    result = pd.DataFrame()
    for key, value in alloc.items():
        result[key] = np.repeat('', 50)
        result[key][:len(value)] = value
    result.to_csv('result.csv')

    rating_data.set_index('fio',inplace=True)
    for key, value in alloc.items():
        for student in value:
            rating_data.loc[student, key] = 'APPLIED'

    rating_data.to_csv('applications.csv')


# INFINITE CYCLE
# CHECKERS -- properties
# NA
# ??
# missing preferences
# inferring them
# ML + MD (Blockchain)