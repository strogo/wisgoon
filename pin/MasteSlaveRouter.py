class MasterSlaveRouter(object):
    def db_for_read(self, model, **hints):
        """
        Reads go to a randomly-chosen slave.
        """
        return 'slave'

    def db_for_write(self, model, **hints):
        """
        Writes always go to master.
        """
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed if both objects are
        in the master/slave pool.
        """
        db_list = ('default', 'slave')
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None

    def allow_migrate(self, db, model):
        """
        All non-auth models end up in this pool.
        """
        return True
