from bnetbase import Variable, Factor, BN
import csv

def multiply_factors(Factors):
    '''Factors is a list of factor objects.
    Return a new factor that is the product of the factors in Factors.
    @return a factor''' 
    ### YOUR CODE HERE ### DONE
    comb_scope = set()
    for factor in Factors:
        comb_scope.update(factor.get_scope())
    possible_assignments = []
    comb_scope = list(comb_scope)
    name = "F({})".format(comb_scope)
    for variable in comb_scope:
        new = []
        for assignment in variable.domain():
            if possible_assignments == []:
                new.append([assignment])
            else:
                for values in possible_assignments:
                    value_copy = values.copy()
                    value_copy.append(assignment)
                    new.append(value_copy)
        possible_assignments = new
    for assignment in possible_assignments:
        value = 1
        for factor in Factors:
            factor_scope = factor.get_scope()
            get_value_prep = []
            for var in factor_scope:
                get_value_prep.append(assignment[comb_scope.index(var)])
            value = value * factor.get_value(get_value_prep)
        assignment.append(value)
    new_factor = Factor(name, comb_scope)
    new_factor.add_values(possible_assignments)
    return new_factor

def restrict_factor(f, var, value):
    '''f is a factor, var is a Variable, and value is a value from var.domain.
    Return a new factor that is the restriction of f by this var = value.
    Don't change f! If f has only one variable its restriction yields a
    constant factor.
    @return a factor''' 
    ### YOUR CODE HERE ### DONE
    scope = f.get_scope()
    possible_assignments = []
    for variable in scope:
        new = []
        for assignment in variable.domain():
            if variable != var or value == assignment:
                if possible_assignments == []:
                    new.append([assignment])
                else:
                    for values in possible_assignments:
                        value_copy = values.copy()
                        value_copy.append(assignment)
                        new.append(value_copy)
        possible_assignments = new
    for item in possible_assignments:
        p = f.get_value(item)
        item.append(p)
        item.remove(value)
    scope.remove(var)
    name = "F({})".format(scope)
    new_factor = Factor(name, scope)
    new_factor.add_values(possible_assignments)
    return new_factor

def sum_out_variable(f, var):
    '''f is a factor, var is a Variable.
    Return a new factor that is the result of summing var out of f, by summing
    the function generated by the product over all values of var.
    @return a factor'''       
    ### YOUR CODE HERE ### DONE
    scope = f.get_scope()
    possible_assignments = []
    for variable in scope:
        new = []
        for assignment in variable.domain():
            if possible_assignments == []:
                new.append([assignment])
            else:
                for values in possible_assignments:
                    value_copy = values.copy()
                    value_copy.append(assignment)
                    new.append(value_copy)
        possible_assignments = new
    index_to_sum = scope.index(var)
    result = {}
    for assignment in possible_assignments:
        assignment_copy = assignment.copy()
        p = f.get_value(assignment_copy)
        del assignment_copy[index_to_sum]
        if tuple(assignment_copy) in result:
            result[tuple(assignment_copy)] += p
        else:
            result[tuple(assignment_copy)] = p
    add_to_factor = []
    for assignment in result:
        assignment_list = list(assignment)
        assignment_list.append(result[assignment])
        add_to_factor.append(assignment_list)
    scope.remove(var)
    name = "F({})".format(scope)
    new_factor = Factor(name, scope)
    new_factor.add_values(add_to_factor)
    return new_factor

def normalize(nums):
    '''num is a list of numbers. Return a new list of numbers where the new
    numbers sum to 1, i.e., normalize the input numbers.
    @return a normalized list of numbers'''
    ### YOUR CODE HERE ### DONE
    sum_of_nums = sum(nums)
    if sum_of_nums == 0:
        normalized_list = [1 / len(nums) for i in range(len(nums))]
        return normalized_list
    normalized_list = []
    for number in nums:
        normalized_list.append(number / sum_of_nums)
    return normalized_list

def min_fill_ordering(Factors, QueryVar):
    '''Factors is a list of factor objects, QueryVar is a query variable.
    Compute an elimination order given list of factors using the min fill heuristic. 
    Variables in the list will be derived from the scopes of the factors in Factors. 
    Order the list such that the first variable in the list generates the smallest
    factor upon elimination. The QueryVar must NOT part of the returned ordering list.
    @return a list of variables''' 
    ### YOUR CODE HERE ### DONE
    scopes = []
    variables = set()
    for factor in Factors:
        factor_scope = factor.get_scope()
        scopes.append(factor_scope)
        variables.update(factor_scope)
    variables = list(variables)
    if QueryVar in variables:
        variables.remove(QueryVar)
    best_order = []
    while variables != []:
        min_var = None
        combined_factor = None
        for var in variables:
            var_combined_scope = set()
            for scope in scopes:
                if var in scope:
                    var_combined_scope.update(scope)
            var_combined_scope.remove(var)
            var_combined_scope = list(var_combined_scope)
            if min_var == None:
                min_var = var
                combined_factor = var_combined_scope
            elif len(var_combined_scope) < len(combined_factor):
                min_var = var
                combined_factor = var_combined_scope
        best_order.append(min_var)
        variables.remove(min_var)
        new_scope = []
        for scope in scopes:
            if not (min_var in scope):
                new_scope.append(scope)
        new_scope.append(combined_factor)
        scopes = new_scope
    return best_order

def VE(Net, QueryVar, EvidenceVars):
    
    """
    Input: Net---a BN object (a Bayes Net)
           QueryVar---a Variable object (the variable whose distribution
                      we want to compute)
           EvidenceVars---a LIST of Variable objects. Each of these
                          variables has had its evidence set to a particular
                          value from its domain using set_evidence.
     VE returns a distribution over the values of QueryVar, i.e., a list
     of numbers, one for every value in QueryVar's domain. These numbers
     sum to one, and the i'th number is the probability that QueryVar is
     equal to its i'th value given the setting of the evidence
     variables. For example if QueryVar = A with Dom[A] = ['a', 'b',
     'c'], EvidenceVars = [B, C], and we have previously called
     B.set_evidence(1) and C.set_evidence('c'), then VE would return a
     list of three numbers. E.g. [0.5, 0.24, 0.26]. These numbers would
     mean that Pr(A='a'|B=1, C='c') = 0.5 Pr(A='a'|B=1, C='c') = 0.24
     Pr(A='a'|B=1, C='c') = 0.26
     @return a list of probabilities, one for each item in the domain of the QueryVar
     """
    ### YOUR CODE HERE ### DONE
    factors = Net.factors()
    restriction_result_factors = []
    for factor in factors:
        result_factor = factor
        for evidence in EvidenceVars:
            factor_scope = result_factor.get_scope()
            if evidence in factor_scope:
                result_factor = restrict_factor(result_factor, evidence, evidence.get_evidence())
        if result_factor.get_scope() != []:
            restriction_result_factors.append(result_factor)
    elim_order = min_fill_ordering(restriction_result_factors, QueryVar)
    for variable in elim_order:
        factors_with_variable = []
        new_resulting_factor = []
        for f in restriction_result_factors:
            f_scope = f.get_scope()
            if variable in f_scope:
                factors_with_variable.append(f)
            else:
                new_resulting_factor.append(f)
        mult_resulting_factor = multiply_factors(factors_with_variable)
        resulting_sum_factor = sum_out_variable(mult_resulting_factor, variable)
        if resulting_sum_factor.get_scope() != []:
            new_resulting_factor.append(resulting_sum_factor)
        restriction_result_factors = new_resulting_factor
    final_factor = multiply_factors(restriction_result_factors)
    result = []
    for assignment in QueryVar.domain():
        result.append(final_factor.get_value([assignment]))
    return normalize(result)

def NaiveBayesModel():
    '''
   NaiveBayesModel returns a BN that is a Naive Bayes model that 
   represents the joint distribution of value assignments to 
   variables in the Adult Dataset from UCI.  Remember a Naive Bayes model
   assumes P(X1, X2,.... XN, Class) can be represented as 
   P(X1|Class)*P(X2|Class)* .... *P(XN|Class)*P(Class).
   When you generated your Bayes Net, assume that the values 
   in the SALARY column of the dataset are the CLASS that we want to predict.
   @return a BN that is a Naive Bayes model and which represents the Adult Dataset. 
    '''
    ### READ IN THE DATA
    input_data = []
    with open('data/adult-dataset.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader, None) #skip header row
        for row in reader:
            input_data.append(row)

    ### DOMAIN INFORMATION REFLECTS ORDER OF COLUMNS IN THE DATA SET
    variable_domains = {
    "Work": ['Not Working', 'Government', 'Private', 'Self-emp'],
    "Education": ['<Gr12', 'HS-Graduate', 'Associate', 'Professional', 'Bachelors', 'Masters', 'Doctorate'],
    "MaritalStatus": ['Not-Married', 'Married', 'Separated', 'Widowed'],
    "Occupation": ['Admin', 'Military', 'Manual Labour', 'Office Labour', 'Service', 'Professional'],    
    "Relationship": ['Wife', 'Own-child', 'Husband', 'Not-in-family', 'Other-relative', 'Unmarried'],
    "Race": ['White', 'Black', 'Asian-Pac-Islander', 'Amer-Indian-Eskimo', 'Other'],
    "Gender": ['Male', 'Female'],
    "Country": ['North-America', 'South-America', 'Europe', 'Asia', 'Middle-East', 'Carribean'],
    "Salary": ['<50K', '>=50K']
    }
    ### YOUR CODE HERE ### DONE
    variable_list = []
    factor_list = []
    for key in variable_domains:
        var = Variable(key, variable_domains[key])
        variable_list.append(var)
    counter = 0
    for key in variable_domains:
        if key != "Salary":
            factor = Factor("P({}|Salary)".format(key), [variable_list[counter], variable_list[-1]])
        else:
            factor = Factor("P({})".format(key), [variable_list[counter]])
        factor_list.append(factor)
        counter += 1
    for entry in input_data:
        for index in range(len(entry)):
            if index != 8:
                curr_value = factor_list[index].get_value([entry[index], entry[-1]])
                factor_list[index].add_values([[entry[index], entry[-1], curr_value + 1]])                
            else:
                curr_value = factor_list[index].get_value([entry[index]])
                factor_list[index].add_values([[entry[index], curr_value + 1]])
    for factor_list_index in range(len(factor_list)):
        if factor_list_index != 8:
            odd_value_sum = sum(factor_list[factor_list_index].values[::2])
            even_value_sum = sum(factor_list[factor_list_index].values[1::2])
            normalize_value = []
            counter = 0
            for value in factor_list[factor_list_index].values:
                if counter == 0:
                    normalize_value.append(value / odd_value_sum)
                    counter = 1
                else:
                    normalize_value.append(value / even_value_sum)
                    counter = 0
            factor_list[factor_list_index].values = normalize_value
        else:
            value_sum = sum(factor_list[factor_list_index].values)
            normalize_value = [value / value_sum for value in factor_list[factor_list_index].values]
            factor_list[factor_list_index].values = normalize_value
    adult_dataset_bn = BN("AdultDatasetBN", variable_list, factor_list)
    return adult_dataset_bn


def Explore(Net, question):
    '''    Input: Net---a BN object (a Bayes Net)
           question---an integer indicating the question in HW4 to be calculated. Options are:
           1. What percentage of the women in the data set end up with a P(S=">=$50K"|E1) that is strictly greater than P(S=">=$50K"|E2)?
           2. What percentage of the men in the data set end up with a P(S=">=$50K"|E1) that is strictly greater than P(S=">=$50K"|E2)?
           3. What percentage of the women in the data set with P(S=">=$50K"|E1) > 0.5 actually have a salary over $50K?
           4. What percentage of the men in the data set with P(S=">=$50K"|E1) > 0.5 actually have a salary over $50K?
           5. What percentage of the women in the data set are assigned a P(Salary=">=$50K"|E1) > 0.5, overall?
           6. What percentage of the men in the data set are assigned a P(Salary=">=$50K"|E1) > 0.5, overall?
           @return a percentage (between 0 and 100)
    ''' 
    ### YOUR CODE HERE ### DONE
    # Read the data
    input_data = []
    with open('data/test-data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader, None) #skip header row
        for row in reader:
            input_data.append(row)
    
    numerator = 0
    denominator = 0
    work_var = Net.get_variable("Work")
    occupation_var = Net.get_variable("Occupation")
    education_var = Net.get_variable("Education")
    relationship_var = Net.get_variable("Relationship")
    gender_var = Net.get_variable("Gender")
    salary_var = Net.get_variable("Salary")
    E1_set = [work_var, occupation_var, education_var, relationship_var]
    E2_set = [work_var, occupation_var, education_var, relationship_var, gender_var]
    for entry in input_data:
        work = entry[0]
        occupation = entry[3]
        education = entry[1]
        relationship = entry[4]
        gender = entry[6]
        salary = entry[8]
        work_var.set_evidence(work)
        occupation_var.set_evidence(occupation)
        education_var.set_evidence(education)
        relationship_var.set_evidence(relationship)
        gender_var.set_evidence(gender)
        if question == 1 and gender == "Female":
            E1_result = VE(Net, salary_var, E1_set)
            E2_result = VE(Net, salary_var, E2_set)
            if E1_result[1] > E2_result[1]:
                numerator += 1
            denominator += 1
        elif question == 2 and gender == "Male":
            E1_result = VE(Net, salary_var, E1_set)
            E2_result = VE(Net, salary_var, E2_set)
            if E1_result[1] > E2_result[1]:
                numerator += 1
            denominator += 1
        elif question == 3 and gender == "Female":
            E1_result = VE(Net, salary_var, E1_set)
            if E1_result[1] > 0.5:
                denominator += 1
                if salary == ">=50K":
                    numerator += 1
        elif question == 4 and gender == "Male":
            E1_result = VE(Net, salary_var, E1_set)
            if E1_result[1] > 0.5:
                denominator += 1
                if salary == ">=50K":
                    numerator += 1
        elif question == 5 and gender == "Female":
            E1_result = VE(Net, salary_var, E1_set)
            if E1_result[1] > 0.5:
                numerator += 1
            denominator += 1
        elif question == 6 and gender == "Male":
            E1_result = VE(Net, salary_var, E1_set)
            if E1_result[1] > 0.5:
                numerator += 1
            denominator += 1
    if denominator == 0:
        return 0
    return numerator/denominator * 100
