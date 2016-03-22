

def convertToString(conf_d, sep=": "):
    assert isinstance(conf_d, dict), "conf_d is not a dictionary type!"
    return "\n".join([k + sep + str(v) for k, v in conf_d.iteritems()])

class Conf():
    def __init__(self, key_name, default_value, assigment_char = ":"):
        self._key_name = key_name
        self._value = default_value
        self._assignment = assigment_char

    def set(self, value):
        self._value = value

    def __str__(self):
        return self._assignment.join([self._key_name, self._value])

class Attribute:
    def __init__(self, attr_type):
        self._attr_type = attr_type
        self._prefix = "pre_"
        self._suffix = "_suffix"
        self._separator = ":"
        self._values = {}

    def setName(self, prefix, suffix):
        self._prefix = prefix
        self._suffix = suffix

    def setSep(self, separator):
        self._separator = separator

    def __setattr__(self, key, value):
        self._values[key] = value

    def __str__(self):
        return "\n".join([self._prefix + k + self._suffix + self._separator + self._values[k] for k in self._values.keys()])

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
            "increase-" + self._conftype  + "s-unit": "percent",
            "decrease-" + self._conftype  + "s-unit": "percent"
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
            "increase-throttled-by-consumed-" + self._conftype + "s-scale": "{ 0.25: 15, 0.5: 25, 1: 50, 2: 75, 5: 100 }"
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
        numChecks_s = convertToString(self._numChecksBeforeScaleDown)
        boolConfs_s = convertToString(self._boolConfigurations, " = ")
        unitConfs_s = convertToString(self._unitConfigurations)
        thresholdConfs_s = convertToString(self._thresholdConfigurations)
        withConfs_s = convertToString(self._withConfigurations)
        throttledConfs_s = convertToString(self._throttledConfigurations)
        provisionedConfs_s = convertToString(self._provisionedConfigurations)

        return header + "\n".join([numChecks_s,
                          boolConfs_s,
                          unitConfs_s,
                          thresholdConfs_s,
                          withConfs_s,
                          throttledConfs_s,
                          provisionedConfs_s
                            ])


class Reads(Configurations):
    def __init__(self):
        Configurations.__init__(self,"read")


class Writes(Configurations):
    def __init__(self):
        Configurations.__init__(self,"write")


class Table():
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

class DDConf:
    def __init__(self):
        self._filename = "dynamic-dynamodb.conf"

if __name__ == "__main__":

    tables_d = {
        "com.curalate.history.item_history": {
            "reads": {
                "throttle": 5,
                "provisioned": {
                    "min": 10,
                    "max": 25
                }
            },
            "writes": {
                "throttle": 5,
                "provisioned": {
                    "min": 5,
                    "max": 25
                }
            }
        },
        "com.curalate.idx_tweets_by_pin": {
            "reads": {
                "throttle": 5,
                "provisioned": {
                    "min": 100,
                    "max": 250
                }
            },
            "writes": {
                "throttle": 5,
                "provisioned": {
                    "min": 10,
                    "max": 40
                }
            }
        },
        "com.curalate.users": {
            "reads": {
                "throttle": 1,
                "numchecks": 6,
                "provisioned": {
                    "min": 10,
                    "max": 300
                }
            },
            "writes": {
                "throttle": 1,
                "provisioned": {
                    "min": 10,
                    "max": 200
                }
            }
        },
        "com.curalate.idx_pins_by_domain": {
            "reads": {
                "throttle": 5,
                "numchecks": 6,
                "provisioned": {
                    "min": 50,
                    "max": 500
                }
            },
            "writes": {
                "throttle": 50,
                "provisioned": {
                    "min": 200,
                    "max": 600
                }
            }
        },
        "com.curalate.imageprocessing.idx_file_id_by_url": {
            "reads": {
                "throttle": 5,
                "numchecks": 6,
                "provisioned": {
                    "min": 600,
                    "max": 1200
                }
            },
            "writes": {
                "throttle": 50,
                "provisioned": {
                    "min": 200,
                    "max": 600
                }
            }
        },
        "com.curalate.imageprocessing.locks": {
            "reads": {
                "throttle": 5,
                "numchecks": 6,
                "provisioned": {
                    "min": 100,
                    "max": 1200
                }
            },
            "writes": {
                "throttle": 50,
                "provisioned": {
                    "min": 250,
                    "max": 1200
                }
            }
        },
        "com.curalate.instagram.comments": {
            "reads": {
                "throttle": 10,
                "numchecks": 6,
                "provisioned": {
                    "min": 2662,
                    "max": 9000
                }
            },
            "writes": {
                "throttle": 5,
                "provisioned": {
                    "min": 1300,
                    "max": 2000
                }
            }
        },
        "com.curalate.deduplication.idx_deduplication_features_by_file_id": {
            "reads": {
                "throttle": 100,
                "numchecks": 6,
                "provisioned": {
                    "min": 1000,
                    "max": 2000
                }
            },
            "writes": {
                "throttle": 5,
                "provisioned": {
                    "min": 100,
                    "max": 200
                }
            }
        },
        "com.curalate.idx_user_lookup": {
            "reads": {
                "throttle": 100,
                "numchecks": 12,
                "provisioned": {
                    "min": 500,
                    "max": 2500
                }
            },
            "writes": {
                "throttle": 5,
                "provisioned": {
                    "min": 10,
                    "max": 30
                }
            }
        },
        "com.curalate.idx_pins_by_board": {
            "reads": {
                "throttle": 200,
                "numchecks": 12,
                "provisioned": {
                    "min": 200,
                    "max": 6000
                }
            },
            "writes": {
                "throttle": 5,
                "provisioned": {
                    "min": 200,
                    "max": 800
                }
            }
        },
        "com.curalate.idx_board_lookup": {
            "reads": {
                "throttle": 200,
                "numchecks": 12,
                "provisioned": {
                    "min": 500,
                    "max": 2500
                }
            },
            "writes": {
                "throttle": 1,
                "provisioned": {
                    "min": 50,
                    "max": 300
                }
            }
        },
        "com.curalate.images": {
            "reads": {
                "throttle": 100,
                "numchecks": 12,
                "provisioned": {
                    "min": 500,
                    "max": 5000
                }
            },
            "writes": {
                "throttle": 5,
                "provisioned": {
                    "min": 100,
                    "max": 300
                }
            }
        },
        "com.curalate.boards": {
            "reads": {
                "throttle": 1000,
                "numchecks": 18,
                "provisioned": {
                    "min": 500,
                    "max": 12000
                }
            },
            "writes": {
                "throttle": 5,
                "provisioned": {
                    "min": 50,
                    "max": 150
                }
            }
        },
        "com.curalate.pin.insights": {
            "reads": {
                "throttle": 100,
                "numchecks": 24,
                "provisioned": {
                    "min": 500,
                    "max": 10000
                }
            },
            "writes": {
                "throttle": 5,
                "provisioned": {
                    "min": 50,
                    "max": 500
                }
            }
        },
        "com.curalate.idx_pins_by_tracking_code": {
            "reads": {
                "throttle": 10,
                "numchecks": 12,
                "provisioned": {
                    "min": 1800,
                    "max": 3000
                }
            },
            "writes": {
                "throttle": 5,
                "provisioned": {
                    "min": 15,
                    "max": 30
                }
            }
        },
        "com.curalate.campaigns.campaign_impressions": {
            "reads": {
                "throttle": 2,
                "numchecks": 12,
                "provisioned": {
                    "min": 50,
                    "max": 400
                }
            },
            "writes": {
                "throttle": 2,
                "provisioned": {
                    "min": 5,
                    "max": 200
                }
            }
        },
        "com.curalate.campaigns.campaign_pins": {
            "reads": {
                "throttle": 2,
                "numchecks": 6,
                "provisioned": {
                    "min": 50,
                    "max": 400
                }
            },
            "writes": {
                "throttle": 2,
                "provisioned": {
                    "min": 5,
                    "max": 20
                }
            }
        },
        "com.curalate.deduplication.blacklisted_fingerprints": {
            "reads": {
                "throttle": 2,
                "numchecks": 6,
                "provisioned": {
                    "min": 10,
                    "max": 200
                }
            },
            "writes": {
                "throttle": 2,
                "provisioned": {
                    "min": 5,
                    "max": 20
                }
            }
        },
        "com.curalate.deduplication.idx_canonical_id_by_file_id": {
            "reads": {
                "throttle": 200,
                "provisioned": {
                    "min": 5000,
                    "max": 25000
                }
            },
            "writes": {
                "throttle": 20,
                "provisioned": {
                    "min": 350,
                    "max": 400
                }
            }
        },
        "com.curalate.deduplication.idx_file_id_by_canonical_id": {
            "reads": {
                "throttle": 2000,
                "provisioned": {
                    "min": 2000,
                    "max": 13000
                }
            },
            "writes": {
                "throttle": 20,
                "provisioned": {
                    "min": 150,
                    "max": 300
                }
            }
        },
        "com.curalate.deduplication.idx_file_id_by_fingerprint": {
            "reads": {
                "throttle": 5,
                "numchecks": 6,
                "provisioned": {
                    "min": 100,
                    "max": 800
                }
            },
            "writes": {
                "throttle": 5,
                "numchecks": 6,
                "provisioned": {
                    "min": 200,
                    "max": 500
                }
            }
        },
        "com.curalate.deduplication.idx_fingerprint_by_hash": {
            "reads": {
                "throttle": 50,
                "numchecks": 6,
                "provisioned": {
                    "min": 10600,
                    "max": 18000
                }
            },
            "writes": {
                "throttle": 5,
                "numchecks": 6,
                "provisioned": {
                    "min": 500,
                    "max": 1000
                }
            }
        },
        "com.curalate.deduplication.representative_file_ids": {
            "reads": {
                "throttle": 50,
                "provisioned": {
                    "min": 1000,
                    "max": 20000
                }
            },
            "writes": {
                "throttle": 5,
                "numchecks": 6,
                "provisioned": {
                    "min": 100,
                    "max": 300
                }
            }
        },
        "com.curalate.facebook_access_tokens": {
            "reads": {
                "throttle": 50,
                "numchecks": 6,
                "provisioned": {
                    "min": 50,
                    "max": 250
                }
            },
            "writes": {
                "throttle": 1,
                "numchecks": 6,
                "provisioned": {
                    "min": 1,
                    "max": 20
                }
            }
        },
        "com.curalate.facebook_rate_limit": {
            "reads": {
                "throttle": 50,
                "numchecks": 6,
                "provisioned": {
                    "min": 10,
                    "max": 60
                }
            },
            "writes": {
                "throttle": 1,
                "numchecks": 6,
                "provisioned": {
                    "min": 1,
                    "max": 20
                }
            }
        },
        "com.curalate.idx_boards_by_user": {
            "reads": {
                "throttle": 1,
                "numchecks": 6,
                "provisioned": {
                    "min": 20,
                    "max": 320
                }
            },
            "writes": {
                "throttle": 1,
                "numchecks": 6,
                "provisioned": {
                    "min": 10,
                    "max": 100
                }
            }
        },
        "com.curalate.idx_pins_by_asin": {
            "reads": {
                "throttle": 1,
                "numchecks": 6,
                "provisioned": {
                    "min": 1,
                    "max": 5
                }
            },
            "writes": {
                "throttle": 1,
                "numchecks": 6,
                "provisioned": {
                    "min": 5,
                    "max": 10
                }
            }
        },
        "com.curalate.idx_pins_by_image": {
            "reads": {
                "throttle": 100,
                "numchecks": 18,
                "provisioned": {
                    "min": 500,
                    "max": 12000
                }
            },
            "writes": {
                "throttle": 10,
                "numchecks": 6,
                "provisioned": {
                    "min": 200,
                    "max": 800
                }
            }
        },
        "com.curalate.imageprocessing.file_meta_data": {
            "reads": {
                "throttle": 100,
                "numchecks": 18,
                "provisioned": {
                    "min": 1000,
                    "max": 20000
                }
            },
            "writes": {
                "throttle": 10,
                "numchecks": 6,
                "provisioned": {
                    "min": 400,
                    "max": 1200
                }
            }
        },
        "com.curalate.imageprocessing.idx_url_by_file_id": {
            "reads": {
                "throttle": 10,
                "numchecks": 6,
                "provisioned": {
                    "min": 50,
                    "max": 300
                }
            },
            "writes": {
                "throttle": 10,
                "numchecks": 6,
                "provisioned": {
                    "min": 200,
                    "max": 700
                }
            }
        },
        "com.curalate.imageprocessing.knobs": {
            "reads": {
                "throttle": 10,
                "numchecks": 6,
                "provisioned": {
                    "min": 10,
                    "max": 30
                }
            },
            "writes": {
                "throttle": 10,
                "numchecks": 6,
                "provisioned": {
                    "min": 1,
                    "max": 20
                }
            }
        },
        "com.curalate.imageprocessing.tags": {
            "reads": {
                "throttle": 5,
                "numchecks": 6,
                "provisioned": {
                    "min": 20,
                    "max": 100
                }
            },
            "writes": {
                "throttle": 5,
                "numchecks": 6,
                "provisioned": {
                    "min": 10,
                    "max": 50
                }
            }
        },
        "com.curalate.imageprocessing.undigestable_images": {
            "reads": {
                "throttle": 1,
                "numchecks": 6,
                "provisioned": {
                    "min": 5,
                    "max": 50
                }
            },
            "writes": {
                "throttle": 1,
                "numchecks": 6,
                "provisioned": {
                    "min": 2,
                    "max": 10
                }
            }
        },
        "com.curalate.instagram.media": {
            "reads": {
                "throttle": 100,
                "numchecks": 18,
                "provisioned": {
                    "min": 15000,
                    "max": 90000
                }
            },
            "writes": {
                "throttle": 15,
                "numchecks": 6,
                "provisioned": {
                    "min": 1500,
                    "max": 3000
                }
            }
        },
        "com.curalate.instagram.users": {
            "reads": {
                "throttle": 10,
                "numchecks": 6,
                "provisioned": {
                    "min": 8000,
                    "max": 24000
                }
            },
            "writes": {
                "throttle": 500,
                "numchecks": 6,
                "provisioned": {
                    "min": 2750,
                    "max": 7000
                }
            }
        },
        "com.curalate.locks": {
            "reads": {
                "throttle": 5,
                "numchecks": 6,
                "provisioned": {
                    "min": 50,
                    "max": 500
                }
            },
            "writes": {
                "throttle": 10,
                "numchecks": 6,
                "provisioned": {
                    "min": 500,
                    "max": 1500
                }
            }
        },
        "com.curalate.microsite.emoji.idx_user_id_by_network_id": {
            "reads": {
                "throttle": 5,
                "numchecks": 6,
                "provisioned": {
                    "min": 5,
                    "max": 50
                }
            },
            "writes": {
                "throttle": 1,
                "numchecks": 6,
                "provisioned": {
                    "min": 2,
                    "max": 10
                }
            }
        },
        "com.curalate.microsite.emoji.users": {
            "reads": {
                "throttle": 5,
                "numchecks": 6,
                "provisioned": {
                    "min": 5,
                    "max": 50
                }
            },
            "writes": {
                "throttle": 1,
                "numchecks": 6,
                "provisioned": {
                    "min": 2,
                    "max": 10
                }
            }
        },
        "com.curalate.pins": {
            "reads": {
                "throttle": 10,
                "numchecks": 24,
                "provisioned": {
                    "min": 10000,
                    "max": 91000
                }
            },
            "writes": {
                "throttle": 10,
                "numchecks": 24,
                "provisioned": {
                    "min": 1000,
                    "max": 4000
                }
            }
        },
        "com.curalate.reliable_counters_simple": {
            "reads": {
                "throttle": 1,
                "numchecks": 6,
                "provisioned": {
                    "min": 2,
                    "max": 10
                }
            },
            "writes": {
                "throttle": 1,
                "numchecks": 6,
                "provisioned": {
                    "min": 50,
                    "max": 1000
                }
            }
        },
        "com.curalate.source_counts": {
            "reads": {
                "throttle": 1000,
                "numchecks": 18,
                "provisioned": {
                    "min": 5000,
                    "max": 20000
                }
            },
            "writes": {
                "throttle": 1,
                "numchecks": 6,
                "provisioned": {
                    "min": 100,
                    "max": 800
                }
            }
        },
        "com.curalate.user_settings": {
            "reads": {
                "throttle": 1,
                "numchecks": 6,
                "provisioned": {
                    "min": 20,
                    "max": 200
                }
            },
            "writes": {
                "throttle": 1,
                "numchecks": 6,
                "provisioned": {
                    "min": 2,
                    "max": 10
                }
            }
        },
        "com.curalate.utils.event_tracking": {
            "reads": {
                "throttle": 1,
                "numchecks": 6,
                "provisioned": {
                    "min": 300,
                    "max": 800
                }
            },
            "writes": {
                "throttle": 1,
                "numchecks": 6,
                "provisioned": {
                    "min": 150,
                    "max": 500
                }
            }
        }
    }

    confFile = open("dynamic-dynamodb.conf", "w")
    for table in tables_d.keys():

        t = Table(table)
        for type in [ "reads", "writes"]:
            confs = tables_d[table][type]
            t.setThrottledConfigurations(type, confs["throttle"])

            if "numchecks" in confs.keys():
                t.setNumChecksBeforeDown(type, confs["numchecks"])

            lower = confs["provisioned"]["min"]
            upper = confs["provisioned"]["max"]
            t.setProvisionedThroughputs(type, lower, upper)

        print "[table: ^" + table + "$]"
        confFile.writelines(["[table: ^" + table + "$]"])
        print t
        confFile.writelines([str(t)])
        print ""
        confFile.writelines([""])
        print ""
        confFile.writelines([""])
    confFile.close()
