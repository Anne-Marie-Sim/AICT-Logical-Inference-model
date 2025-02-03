import itertools

class Sentence():
    def evaluate(self, model):
        """Evaluates the logical sentence."""
        raise Exception("nothing to evaluate")

    def formula(self):
        """Returns string formula representing logical sentence."""
        return ""

    def symbols(self):
        """Returns a set of all symbols in the logical sentence."""
        return set()

    @classmethod
    def validate(cls, sentence):
        if not isinstance(sentence, Sentence):
            raise TypeError("must be a logical sentence")

    @classmethod
    def parenthesize(cls, s):
        """Parenthesizes an expression if not already parenthesized."""
        def balanced(s):
            """Checks if a string has balanced parentheses."""
            count = 0
            for c in s:
                if c == "(":
                    count += 1
                elif c == ")":
                    if count <= 0:
                        return False
                    count -= 1
            return count == 0
        if not len(s) or s.isalpha() or (
            s[0] == "(" and s[-1] == ")" and balanced(s[1:-1])
        ):
            return s
        else:
            return f"({s})"

class Symbol(Sentence):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.name == other.name

    def __hash__(self):
        return hash(("symbol", self.name))

    def __repr__(self):
        return self.name

    def evaluate(self, model):
        try:
            return bool(model[self.name])
        except KeyError:
            raise Exception(f"variable {self.name} not in model")

    def formula(self):
        return self.name

    def symbols(self):
        return {self.name}

class Not(Sentence):
    def __init__(self, operand):
        Sentence.validate(operand)
        self.operand = operand

    def __eq__(self, other):
        return isinstance(other, Not) and self.operand == other.operand

    def __hash__(self):
        return hash(("not", hash(self.operand)))

    def __repr__(self):
        return f"Not({self.operand})"

    def evaluate(self, model):
        return not self.operand.evaluate(model)

    def formula(self):
        return "¬" + Sentence.parenthesize(self.operand.formula())

    def symbols(self):
        return self.operand.symbols()

class And(Sentence):
    def __init__(self, *conjuncts):
        for conjunct in conjuncts:
            Sentence.validate(conjunct)
        self.conjuncts = list(conjuncts)

    def __eq__(self, other):
        return isinstance(other, And) and self.conjuncts == other.conjuncts

    def __hash__(self):
        return hash(
            ("and", tuple(hash(conjunct) for conjunct in self.conjuncts))
        )

    def __repr__(self):
        conjunctions = ", ".join(
            [str(conjunct) for conjunct in self.conjuncts]
        )
        return f"And({conjunctions})"

    def add(self, conjunct):
        Sentence.validate(conjunct)
        self.conjuncts.append(conjunct)

    def evaluate(self, model):
        return all(conjunct.evaluate(model) for conjunct in self.conjuncts)

    def formula(self):
        if len(self.conjuncts) == 1:
            return self.conjuncts[0].formula()
        return " ∧ ".join([Sentence.parenthesize(conjunct.formula())
                           for conjunct in self.conjuncts])

    def symbols(self):
        return set.union(*[conjunct.symbols() for conjunct in self.conjuncts])

class Implication(Sentence):
    def __init__(self, antecedent, consequent):
        Sentence.validate(antecedent)
        Sentence.validate(consequent)
        self.antecedent = antecedent
        self.consequent = consequent

    def __eq__(self, other):
        return (isinstance(other, Implication)
                and self.antecedent == other.antecedent
                and self.consequent == other.consequent)

    def __hash__(self):
        return hash(("implies", hash(self.antecedent), hash(self.consequent)))

    def __repr__(self):
        return f"Implication({self.antecedent}, {self.consequent})"

    def evaluate(self, model):
        return ((not self.antecedent.evaluate(model))
                or self.consequent.evaluate(model))

    def formula(self):
        antecedent = Sentence.parenthesize(self.antecedent.formula())
        consequent = Sentence.parenthesize(self.consequent.formula())
        return f"{antecedent} => {consequent}"

    def symbols(self):
        return set.union(self.antecedent.symbols(), self.consequent.symbols())

class TrafficRules:
    def __init__(self):
        # Define basic propositions
        self.speed_limit = Symbol("SpeedLimit")
        self.residential = Symbol("Residential")
        self.highway = Symbol("Highway")
        self.red_light = Symbol("RedLight")
        self.at_intersection = Symbol("AtIntersection")
        self.vehicle_moving = Symbol("VehicleMoving")
        self.signal_change = Symbol("SignalChange")
        self.signal_used = Symbol("SignalUsed")
        self.one_way = Symbol("OneWay")
        self.wrong_direction = Symbol("WrongDirection")
        self.stop_sign = Symbol("StopSign")
        self.complete_stop = Symbol("CompleteStop")
        self.no_parking = Symbol("NoParking")
        self.is_parked = Symbol("IsParked")
        self.no_overtaking = Symbol("NoOvertaking")
        self.is_overtaking = Symbol("IsOvertaking")
        self.location_a = Symbol("LocationA")
        self.location_b = Symbol("LocationB")
        
        # Define rules and their corresponding violations
        self.rules = []
        self._initialize_rules()

    def _initialize_rules(self):
        """Initialize all traffic rules"""
        self.rules = [
            # Speed violations
            (And(self.speed_limit, self.residential), "Speed violation in residential area"),
            (And(self.speed_limit, self.highway), "Speed violation on highway"),
            
            # Red light violations
            (And(self.red_light, self.at_intersection, self.vehicle_moving), "Red light violation"),
            
            # Lane change violations
            (And(self.signal_change, Not(self.signal_used)), "Lane change violation"),
            
            # One-way violations
            (And(self.one_way, self.wrong_direction), "Wrong way violation"),
            
            # Stop sign violations
            (And(self.stop_sign, Not(self.complete_stop)), "Stop sign violation"),
            
            # Parking violations
            (And(self.no_parking, self.is_parked), "Parking violation"),
            
            # Overtaking violations
            (And(self.no_overtaking, self.is_overtaking), "Overtaking violation"),
            
            # Location consistency
            (And(self.location_a, self.location_b), "Location inconsistency")
        ]

    def check_violations(self, scenario):
       
        violations = []
        
        # Create mapping from snake_case to CamelCase
        key_mapping = {
            'speed_limit': 'SpeedLimit',
            'residential': 'Residential',
            'highway': 'Highway',
            'red_light': 'RedLight',
            'at_intersection': 'AtIntersection',
            'vehicle_moving': 'VehicleMoving',
            'signal_change': 'SignalChange',
            'signal_used': 'SignalUsed',
            'one_way': 'OneWay',
            'wrong_direction': 'WrongDirection',
            'stop_sign': 'StopSign',
            'complete_stop': 'CompleteStop',
            'no_parking': 'NoParking',
            'is_parked': 'IsParked',
            'no_overtaking': 'NoOvertaking',
            'is_overtaking': 'IsOvertaking',
            'location_a': 'LocationA',
            'location_b': 'LocationB'
        }
        
        # Convert scenario keys to match symbol names
        model = {
            key_mapping[key]: value 
            for key, value in scenario.items()
            if key in key_mapping
        }
        
        # Check each rule
        for rule, violation_msg in self.rules:
            try:
                if rule.evaluate(model):
                    violations.append(violation_msg)
            except Exception as e:
                continue  # Skip errors silently for cleaner output
                
        return violations

def main():
    # Initialize traffic rules system
    traffic_system = TrafficRules()
    
    # Define specific test scenarios, including both violation and non-violation cases
    specific_scenarios = [
        # Non-violation scenarios
        {
            "name": "Normal Highway Driving",
            "scenario": {
                'speed_limit': False,  # Not exceeding speed limit
                'residential': False,
                'highway': True,
                'red_light': False,
                'at_intersection': False,
                'vehicle_moving': True,
                'signal_change': False,
                'signal_used': True,
                'one_way': False,
                'wrong_direction': False,
                'stop_sign': False,
                'complete_stop': True,
                'no_parking': False,
                'is_parked': False,
                'no_overtaking': False,
                'is_overtaking': False,
                'location_a': True,
                'location_b': False
            }
        },
        {
            "name": "Proper Stop at Red Light",
            "scenario": {
                'speed_limit': False,
                'residential': True,
                'highway': False,
                'red_light': True,
                'at_intersection': True,
                'vehicle_moving': False,  # Stopped at red light
                'signal_change': False,
                'signal_used': True,
                'one_way': False,
                'wrong_direction': False,
                'stop_sign': False,
                'complete_stop': True,
                'no_parking': False,
                'is_parked': False,
                'no_overtaking': False,
                'is_overtaking': False,
                'location_a': True,
                'location_b': False
            }
        },
        {
            "name": "Legal Parking",
            "scenario": {
                'speed_limit': False,
                'residential': True,
                'highway': False,
                'red_light': False,
                'at_intersection': False,
                'vehicle_moving': False,
                'signal_change': False,
                'signal_used': True,
                'one_way': False,
                'wrong_direction': False,
                'stop_sign': False,
                'complete_stop': True,
                'no_parking': False,  # Not a no-parking zone
                'is_parked': True,    # Parked legally
                'no_overtaking': False,
                'is_overtaking': False,
                'location_a': True,
                'location_b': False
            }
        },
        {
            "name": "Proper Lane Change",
            "scenario": {
                'speed_limit': False,
                'residential': True,
                'highway': False,
                'red_light': False,
                'at_intersection': False,
                'vehicle_moving': True,
                'signal_change': True,
                'signal_used': True,   # Using signal for lane change
                'one_way': False,
                'wrong_direction': False,
                'stop_sign': False,
                'complete_stop': False,
                'no_parking': False,
                'is_parked': False,
                'no_overtaking': False,
                'is_overtaking': False,
                'location_a': True,
                'location_b': False
            }
        },
        {
            "name": "Speeding in Residential Area",
            "scenario": {
                'speed_limit': True,
                'residential': True,
                'highway': False,
                'red_light': False,
                'at_intersection': False,
                'vehicle_moving': True,
                'signal_change': False,
                'signal_used': False,
                'one_way': False,
                'wrong_direction': False,
                'stop_sign': False,
                'complete_stop': False,
                'no_parking': False,
                'is_parked': False,
                'no_overtaking': False,
                'is_overtaking': False,
                'location_a': False,
                'location_b': False
            }
        },
        {
            "name": "Running Red Light",
            "scenario": {
                'speed_limit': False,
                'residential': False,
                'highway': False,
                'red_light': True,
                'at_intersection': True,
                'vehicle_moving': True,
                'signal_change': False,
                'signal_used': False,
                'one_way': False,
                'wrong_direction': False,
                'stop_sign': False,
                'complete_stop': False,
                'no_parking': False,
                'is_parked': False,
                'no_overtaking': False,
                'is_overtaking': False,
                'location_a': False,
                'location_b': False
            }
        },
        {
            "name": "Illegal Parking and Stop Sign Violation",
            "scenario": {
                'speed_limit': False,
                'residential': False,
                'highway': False,
                'red_light': False,
                'at_intersection': False,
                'vehicle_moving': False,
                'signal_change': False,
                'signal_used': False,
                'one_way': False,
                'wrong_direction': False,
                'stop_sign': True,
                'complete_stop': False,
                'no_parking': True,
                'is_parked': True,
                'no_overtaking': False,
                'is_overtaking': False,
                'location_a': False,
                'location_b': False
            }
        },
        {
            "name": "Wrong Way on One-Way Street",
            "scenario": {
                'speed_limit': False,
                'residential': False,
                'highway': False,
                'red_light': False,
                'at_intersection': False,
                'vehicle_moving': True,
                'signal_change': False,
                'signal_used': False,
                'one_way': True,
                'wrong_direction': True,
                'stop_sign': False,
                'complete_stop': False,
                'no_parking': False,
                'is_parked': False,
                'no_overtaking': False,
                'is_overtaking': False,
                'location_a': False,
                'location_b': False
            }
        }
    ]

    print("Testing specific scenarios:")
    for scenario_info in specific_scenarios:
        print(f"\nScenario: {scenario_info['name']}")
        print("Active conditions:")
        active_conditions = [key.replace('_', ' ').title() for key, value in scenario_info['scenario'].items() if value]
        if active_conditions:
            for condition in active_conditions:
                print(f"- {condition}")
        else:
            print("- None")
        
        violations = traffic_system.check_violations(scenario_info['scenario'])
        if violations:
            print("\nViolations detected:")
            for violation in violations:
                print(f"- {violation}")
        else:
            print("\nNo violations detected")
        print("-" * 50)

if __name__ == "__main__":
    main()