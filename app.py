import os
from app import app

#----------------------------------------
# launch
#----------------------------------------

if __name__ == "__main__":

	port = int(os.environ.get("PORT", 5050))
	app.run(host='localhost', port=port, debug=True)
	#app.run(ssl_context='adhoc')

