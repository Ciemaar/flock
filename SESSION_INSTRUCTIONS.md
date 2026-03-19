# Session Instructions

This file documents the initial instructions and interaction patterns provided in this session. These instructions can be used as a prompt to establish a rigorous planning and execution workflow in future sessions.

## The Prompt

```markdown
Before making any changes you will start a deep planning mode. You will interact with me to fully understand my requirements. You should be thoughtful and think about what I am trying to achieve.

Your initial goals are:
1. Have absolute certainty of my expectations and goals before you start working on the plan.
2. Even if you think you have clarity on the task, ask me to confirm your assumptions in the form of questions.
3. Remember, you are asking questions - not having me approve a plan. The plan approval comes AFTER you ask these questions.
4. Ask as many questions and take as many turns as you need. You should have zero doubt about the task at hand. Test and verify every assumption you have made.
5. You should only ask questions about the task and questions that clarify my desires. Questions that you can derive from the code like ("what file does this logic live in?") can be asked but are discouraged.
6. After I respond to your questions, you may have more new questions. Think about my answers and reflect on what other questions you might have. Do this as often as you need. Remember in this planning mode, it is your utmost responsibility to make sure the requirements are crystal clear.
7. Always use the `request_user_input` and `message_user` tools to communicate with me and ask me questions.
8. When you are absolutely certain that you fully understand the task, create a plan using the `set_plan` tool as described above.
9. Once the plan is created and approved, proceed with execution autonomously. Do not ask for confirmation or additional questions unless absolutely necessary. Trust your plan and execute it.
```

## Task Example

Following the general instructions, a specific task should be provided. For example:

```markdown
The task I need you to solve is the following:
As much as possible implement the flock objects in terms of closure_collector objects identify any cases where this is difficult or complex to do and suggest any additions to closure_collector that would allow a simpler implementation.
```

## Additional Context from this Session

During the deep planning mode, the following clarifications were made which guided the implementation:

> "Hmm actually I want to add mapping support to closure_collector, let's create a ClosureMapping and, if needed, a ClosureList. FlockDict and FlockList will then inherit from, or if necessary, wrap this to provide their existing interface."

This highlighted the importance of asking clarifying questions before starting the plan, as it shifted the approach from merely rewriting `flock` internals to actively extending the newer `closure_collector` library to provide native mapping and sequence support, which `flock` then inherited.
