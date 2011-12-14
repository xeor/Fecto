from django.core.cache import cache

from apps.siteconfig import models

# FIXME
#  - Make sure it caches the config for a long time! Refresh the cache manually if it changes, TEST

class Conf:
    def _getDbObj(self, confType, name, app):
        if not hasattr(models, confType):
            return false

        dbObj = getattr(models, confType)

        try:
            return True, dbObj.objects.get(name=name, app=app)
        except dbObj.DoesNotExist:
            return False, dbObj # We should return an empty dbObj we can populate if we want


    def add(self, confType, name, appName = '', default = '', permissions = '', description = ''):
        dbObjExists, dbObj = self._getDbObj(confType, name, appName)
        if dbObjExists:
            return False

        dbObj(app=appName, name=name, value=default, default=default, permission=permissions, description=description).save()
        return True

    def get(self, confType, name, app):
        value = cache.get('conf_%s_%s' % (app, name), None)
        if not value:
            dbObjExists, dbObj = self._getDbObj(confType, name, app)

            if not dbObjExists:
                return False

            varType = dbObj.varType

            if varType == 'text':
                value = dbObj.value.strip()
            if varType == 'newlineArray':
                value = dbObj.value.split('\n')
                value = [ x.strip() for x in value ]

            cache.set('%s_%s' % (app, name), value, 60*60*24)

        return value

    def updateInfo(self, confType, name, appName = None, default = None, description = None):
        dbObjExists, dbObj = self._getDbObj(confType, name, appName)

        if not dbObjExists:
            return False

        changes = []

        if (default) and (dbObj.default != default):
            dbObj.default = default
            changes.append('default')

        if (description) and (dbObj.description != description):
            dbObj.description = description
            changes.append('description')

        if changes:
            dbObj.save()
            return changes
        else:
            return False
