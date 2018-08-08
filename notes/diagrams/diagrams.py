from fsm import FSM

def explain():
    fsm = FSM({
        'browser' ,
        'flask' ,
        'views' ,
        'domain' ,
        'drivers',
        'models' ,
        'sqlalchemy' ,
        'sqlite' ,
        'jinja',
        'red = performing action',
        'green = rendering page', 
    })
    fsm.fail( 'browser', 'flask', 'http requests')
    fsm.fail( 'flask', 'views', 'url routing')
    fsm.fail( 'views', 'domain', 'domain commands')
    fsm.fail( 'domain', 'models', 'set model state')
    fsm.fail( 'domain', 'drivers', 'set hardware state')
    fsm.fail( 'models', 'sqlalchemy', 'manage db session',)
    fsm.fail( 'sqlalchemy', 'sqlite', 'SQL',)
    fsm.success( 'views', 'models', 'get model state')
    fsm.success( 'models', 'sqlalchemy', 'query',)
    fsm.success( 'sqlalchemy', 'sqlite', 'SQL',)
    fsm.success( 'sqlite', 'sqlalchemy', 'rows',)
    fsm.success( 'sqlalchemy', 'models', 'models',)
    fsm.success( 'models','views', 'models')
    fsm.success( 'views', 'jinja', 'templating context')
    fsm.success( 'jinja', 'flask', 'html')
    fsm.success( 'flask', 'browser', 'http response')
    fsm.save(name='agua_relays_explanation')

def example():
    fsm = FSM({
        'browser' ,
        'flask' ,
        'views' ,
        'domain' ,
        'drivers',
        'models' ,
        'sqlalchemy' ,
        'sqlite' ,
        'jinja',
        'red = performing action',
        'green = rendering page', 
    })
    fsm.fail( 'browser', 'flask', 'POST /relays')
    fsm.fail( 'flask', 'views', 'views.relay')
    fsm.fail( 'views', 'domain', 'set_relay')
    fsm.fail( 'domain', 'models', 'relay.update')
    fsm.fail( 'domain', 'drivers', 'mod4ko.send')
    fsm.fail( 'models', 'sqlalchemy', 'session.add',)
    fsm.fail( 'sqlalchemy', 'sqlite', 'SQL UPDATE',)
    fsm.success( 'views', 'sqlalchemy', 'Relay.query')
    fsm.success( 'sqlalchemy', 'sqlite', 'SQL SELECT',)
    fsm.success( 'sqlite', 'sqlalchemy', 'rows',)
    fsm.success( 'sqlalchemy', 'views', 'models',)
    fsm.success( 'views', 'jinja', 'context')
    fsm.success( 'jinja', 'flask', 'html')
    fsm.success( 'flask', 'browser', 'http response')
    fsm.save(name='agua_relays_example')

def edit_schema():
    fsm = FSM({
        'terminal' ,
        'flask-migrate' ,
        'alembic',
        'models',
        'sqlalchemy' ,
        'sqlite' ,
    })
    fsm.transition('terminal', 'flask-migrate', 'flask db migrate/upgrade')
    fsm.transition('flask-migrate', 'alembic', 'create/run migration scripts')
    fsm.transition('alembic', 'models', 'detect model changes')
    fsm.transition('alembic', 'sqlalchemy', 'db alterations')
    fsm.transition('sqlalchemy', 'sqlite', 'sql')
    fsm.save(name='example_migrations')

def explain_nodered():
    fsm = FSM({
        'browser' ,
        'node-red' ,
        'spi-din',
        'sqlite' ,
        'db manager'
    })
    fsm.transition('browser', 'node-red', 'http request')
    fsm.transition('node-red', 'browser', 'http request')
    fsm.transition('node-red', 'node-red', 'flow control and javascript functions')
    fsm.transition('node-red', 'spi-din', 'widgetlords node')
    fsm.transition('node-red', 'sqlite', 'sqlite node')
    fsm.transition('db manager', 'sqlite', 'manual modificatin')
    fsm.save(name='nodered_relays_explanation')

explain_nodered()
