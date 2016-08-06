from decimal import Decimal

class RecommendedNutritionalIntake():
    """
    Class for defining the recommended nutriotional inatake. To create a new
    recommendation create an istance of this class, passing the desired values
    as arguments.
    """

    def __init__(self, protein, carbs, fat, calories):
        self._protein = protein
        self._carbs = carbs
        self._fat = fat
        self._calories = calories

    @property
    def protein(self):
        return self._protein

    @property
    def carbs(self):
        return self._carbs
    
    @property
    def fat(self):
        return self._fat
    
    @property
    def calories(self):
        return self._calories
        
CAL2000 = RecommendedNutritionalIntake(protein=50, carbs=300,
    fat=65, calories=2000)

# Note for protein: it's 62.5g rounded to 65g
CAL2500 = RecommendedNutritionalIntake(protein=65, carbs=375,
    fat=80, calories=2500)