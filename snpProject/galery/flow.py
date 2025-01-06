from viewflow import this
from viewflow.workflow import flow
from viewflow.workflow.flow.views import CreateProcessView, UpdateProcessView
from .models import Photo, PhotoModerationProcess



class PhotoModerationProcessFlow(flow.Flow):
    process_class = PhotoModerationProcess

    start = (
        flow.Start(
            CreateProcessView,
            fields=["photo"] 
        ).Next(this.approve)
    )

    approve = (
        flow.View(
            UpdateProcessView,
            fields=["approved"]  
        ).Next(this.check_approve)
    )

    check_approve = (
        flow.If(lambda activation: activation.process.approved)
        .Then(this.end)
        .Else(this.reject)
    )

    reject = (
        flow.View(
            UpdateProcessView,
            fields=["rejected"] 
        ).Next(this.end)
    )

    end = flow.End()
