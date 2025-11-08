class ReasoningPipeline:
    def __init__(self):
        self.stages = [
            ProblemAnalysisStage(),
            SolutionPlanningStage(),
            CalculationStage(),
            VerificationStage()
        ]
    
    def process(self, problem):
        context = {'problem': problem, 'results': []}
        
        for stage in self.stages:
            context = stage.execute(context)
            if not context['success']:
                break
        
        return context['final_result']