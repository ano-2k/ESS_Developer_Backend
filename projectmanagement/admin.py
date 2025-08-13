from django.contrib import admin
from .models import Project, Task, Role,Team,TaskLog,TaskDocument,TaskEmpDocument

admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Role)
admin.site.register(TaskDocument)
admin.site.register(TaskLog)
admin.site.register(Team)
admin.site.register(TaskEmpDocument)