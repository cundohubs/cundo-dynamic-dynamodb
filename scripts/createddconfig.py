import json
import argparse


def convert_to_string(conf_d, sep=": "):
    assert isinstance(conf_d, dict), "conf_d is not a dictionary type!"
    return "\n".join([k + sep + str(v) for k, v in conf_d.iteritems()])


class Configurations:
    def __init__(self, conf_type):
        self._conftype = conf_type
        self._configurations = {}

        self._numChecksBeforeScaleDown = {
            "num-" + self._conftype + "-checks-before-scale-down": "12"
        }
        self._boolConfigurations = {
            "enable-" + self._conftype + "s-up-scaling": "true",
            "enable-" + self._conftype + "s-down-scaling": "false"
        }
        self._unitConfigurations = {
            "increase-" + self._conftype + "s-unit": "percent",
            "decrease-" + self._conftype + "s-unit": "percent"
        }
        self._thresholdConfigurations = {
            self._conftype + "s-upper-threshold": "80",
            self._conftype + "s-lower-threshold": "30"
        }
        self._withConfigurations = {
            "increase-" + self._conftype + "s-with": "50",
            "decrease-" + self._conftype + "s-with": "50"
        }
        self._throttledConfigurations = {
            "throttled-" + self._conftype + "-upper-threshold": "100",
            "increase-throttled-by-consumed-" + self._conftype + "s-unit": "percent",
            "increase-throttled-by-consumed-" + self._conftype + "s-scale":
                "{ 0.25: 15, 0.5: 25, 1: 50, 2: 75, 5: 100 }"
        }
        self._provisionedConfigurations = {
            "min-provisioned-" + self._conftype + "s": "1000",
            "max-provisioned-" + self._conftype + "s": "5000"
        }

    def setNumChecksBeforeDown(self, checks):
        self._numChecksBeforeScaleDown = {
            "num-" + self._conftype + "-checks-before-scale-down": checks
        }

    def setUnits(self, increaseUnits, decreaseUnits):
        self._unitConfigurations["increase-" + self._conftype + "s-unit": ] = increaseUnits
        self._unitConfigurations["decrease-" + self._conftype + "s-unit"] = decreaseUnits

    def setThresholds(self, upperThreshold, lowerThreshold):
        self._thresholdConfigurations[self._conftype + "-upper-threshold"] = upperThreshold
        self._thresholdConfigurations[self._conftype + "-lower-threshold"] = lowerThreshold

    def setWithConfigurations(self, increase, decrease):
        self._withConfigurations["increase-" + self._conftype + "-with"] = increase
        self._withConfigurations["decrease-" + self._conftype + "-with"] = decrease

    def setThrottledConfigurations(self, throttle):
        self._throttledConfigurations["throttled-" + self._conftype + "-upper-threshold"] = throttle

    def setProvisionedThroughputs(self, minimum, maximum):
        self._provisionedConfigurations["min-provisioned-" + self._conftype + "s"] = minimum
        self._provisionedConfigurations["max-provisioned-" + self._conftype + "s"] = maximum

    def  __str__(self):
        header = """\n# #########\n# %s provisioning configuration\n#\n""" % (self._conftype.title())
        # num_checks_s is the count of 5-min increments to wait before scaling a table down
        # num_checks_s = 1 means scaling will occur in 5 minutes after hitting below the scale-down
        #    threshold. A low number means that you'd exhaust the daily limit of 4 scale-downs on a table
        #    very quickly... so best to keep this number closer to 24 (24 x 5 = 120 mins)
        num_checks_s = convert_to_string(self._numChecksBeforeScaleDown)
        bool_confs_s = convert_to_string(self._boolConfigurations, " = ")
        unit_confs_s = convert_to_string(self._unitConfigurations)
        threshold_confs_s = convert_to_string(self._thresholdConfigurations)
        with_confs_s = convert_to_string(self._withConfigurations)
        throttled_confs_s = convert_to_string(self._throttledConfigurations)
        provisioned_confs_s = convert_to_string(self._provisionedConfigurations)

        return header + "\n".join([num_checks_s,
                                   bool_confs_s,
                                   unit_confs_s,
                                   threshold_confs_s,
                                   with_confs_s,
                                   throttled_confs_s,
                                   provisioned_confs_s
                                   ])


class Reads(Configurations):
    def __init__(self):
        Configurations.__init__(self,"read")


class Writes(Configurations):
    def __init__(self):
        Configurations.__init__(self,"write")


class Table:
    def __init__(self, table_name):
        self._table_name = table_name
        self._reads = Reads()
        self._writes = Writes()
        self._types = {
            "reads": self._reads,
            "writes": self._writes
        }

    def setNumChecksBeforeDown(self, type, checks):
        self._types[type].setNumChecksBeforeDown(checks)

    def setProvisionedThroughputs(self, type, minimum, maximum):
        self._types[type].setProvisionedThroughputs(minimum, maximum)

    def setThrottledConfigurations(self, type, throttle):
        assert isinstance(throttle, int)
        self._types[type].setThrottledConfigurations(throttle)

    def __str__(self):
        return "\n".join([str(self._reads), str(self._writes)])


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Curalate json-to-conf file for DynamicDynamoDB')

    parser.add_argument('-j','--json', action="store", type=str, help='path and filename of json file')
    parser.add_argument('-o','--output', action="store", type=str,
                        help='filename to create', default='dynamic-dynamodb.conf')
    parser.parse_known_args(['json'])
    args = parser.parse_args()

    with open(args.json) as json_file:
        tables_json = json.load(json_file)

        confFile = open(args.output, "w")
        for table in tables_json.keys():

            t = Table(table)
            for type in [ "reads", "writes"]:
                confs = tables_json[table][type]
                t.setThrottledConfigurations(type, confs["throttle"])

                if "numchecks" in confs.keys():
                    t.setNumChecksBeforeDown(type, confs["numchecks"])

                lower = confs["provisioned"]["min"]
                upper = confs["provisioned"]["max"]
                t.setProvisionedThroughputs(type, lower, upper)

            # print "[table: ^" + table + "$]"
            confFile.writelines(["[table: ^" + table + "$]"])
            # print t
            confFile.writelines([str(t)])
            # print ""
            confFile.writelines([""])
            # print ""
            confFile.writelines([""])
        confFile.close()
