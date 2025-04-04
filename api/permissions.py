from rest_framework.permissions import BasePermission
from api.models import Issue, Contributor, Project


class IsAuthor(BasePermission):
    message = "Vous devez être l'auteur"

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author


class IsContributor(BasePermission):

    message = 'Vous ne faites pas partie du projet'

    def has_permission(self, request, view):
        if view.action == 'create':
            if 'issue' in request.data:
                # Tests for project
                if Issue.objects.filter(pk=request.data['issue']).exists():
                    project = Issue.objects.get(pk=request.data['issue']).project
                else:
                    self.message = 'Création impossible'
                    return False
            elif 'project' in request.data:
                # Tests for issue
                if 'assigned_user' in request.data:
                    if not Contributor.objects.filter(
                        user=request.data['assigned_user'],
                            project=request.data['project']).exists():
                        self.message = 'Création impossible'
                        return False
                project = Project.objects.get(pk=request.data['project'])
            return Contributor.objects.filter(project=project, user=request.user).exists()
        return True

    def has_object_permission(self, request, view, obj):
        if 'project' in request.path:
            project = obj
        elif 'issue' in request.path:
            project = obj.project
        elif 'comment' in request.path:
            project = obj.issue.project
        return Contributor.objects.filter(project=project, user=request.user).exists()


class IsNotAllowedToList(BasePermission):

    message = 'Impossible de lister'

    def has_permission(self, request, view):
        return view.action != 'list'
