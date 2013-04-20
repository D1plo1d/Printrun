# Add 2 jobs
curl -i --user admin:admin -F job=@./testfiles/quick-test.gcode http://localhost:8888/jobs
curl -i --user admin:admin -F job=@./testfiles/quick-test.gcode http://localhost:8888/jobs
curl -i --user admin:admin -F job=@./testfiles/quick-test.gcode http://localhost:8888/jobs

# Update Job #1
curl -X PUT -F job[position]=200 http://localhost:8888/jobs/1

# Delete Job #1
curl -X DELETE http://localhost:8888/jobs/1

# Start the print queue (DON'T DO THIS WITH A REAL PRINTER ATTACHED!!)
curl --user admin:admin -X PUT http://localhost:8888/jobs/print
