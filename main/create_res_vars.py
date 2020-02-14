import json

res_vars = {
            "EZE": {
                "trafo": {
                    "buslv": {
                        "Sym": [
                            "m:u1:buslv",
                            "m:I1:buslv",
                            "m:I1P:buslv",
                            "m:I1Q:buslv"
                        ],
                        "ULE": [
                            "n:u:buslv:A",
                            "n:u:buslv:B",
                            "n:u:buslv:C"
                        ],
                        "Unsym": [
                            "n:ul:buslv:A",
                            "n:ul:buslv:B",
                            "n:ul:buslv:C",
                            "m:I:buslv:A",
                            "m:I:buslv:B",
                            "m:I:buslv:C",
                            "m:I1P:buslv",
                            "m:I1Q:buslv"
                        ]
                    }
                },
                "line": {
                    "bus2": {
                        "Sym": [
                            "m:u1:bus2",
                            "m:I1:bus2",
                            "m:I1P:bus2",
                            "m:I1Q:bus2"
                        ],
                        "ULE": [
                            "n:u:bus2:A",
                            "n:u:bus2:B",
                            "n:u:bus2:C"
                        ],
                        "Unsym": [
                            "n:ul:bus2:A",
                            "n:ul:bus2:B",
                            "n:ul:bus2:C",
                            "m:I:bus2:A",
                            "m:I:bus2:B",
                            "m:I:bus2:C",
                            "m:I1P:bus2",
                            "m:I1Q:bus2"
                        ]
                    }
                }
            },
            "MS": {
                "trafo": {
                    "bushv": {
                        "Sym": [
                            "m:u1:bushv",
                            "m:I1:bushv",
                            "m:I1P:bushv",
                            "m:I1Q:bushv"
                        ],
                        "Unsym": [
                            "n:ul:bushv:A",
                            "n:ul:bushv:B",
                            "n:ul:bushv:C",
                            "m:I:bushv:A",
                            "m:I:bushv:B",
                            "m:I:bushv:C",
                            "m:I1P:bushv",
                            "m:I1Q:bushv"
                        ]
                    }
                },
                "line": {
                    "bus2": {
                        "Sym": [
                            "m:u1:bus2",
                            "m:I1:bus2",
                            "m:I1P:bus2",
                            "m:I1Q:bus2"
                        ],
                        "Unsym": [
                            "n:ul:bus2:A",
                            "n:ul:bus2:B",
                            "n:ul:bus2:C",
                            "m:I:bus2:A",
                            "m:I:bus2:B",
                            "m:I:bus2:C",
                            "m:I1P:bus2",
                            "m:I1Q:bus2"
                        ]
                    },
                    "bus1": {
                        "Sym": [
                            "m:u1:bus1",
                            "m:I1:bus1",
                            "m:I1P:bus1",
                            "m:I1Q:bus1"
                        ],
                        "Unsym": [
                            "n:ul:bus1:A",
                            "n:ul:bus1:B",
                            "n:ul:bus1:C",
                            "m:I:bus1:A",
                            "m:I:bus1:B",
                            "m:I:bus1:C",
                            "m:I1P:bus1",
                            "m:I1Q:bus1"
                        ]
                    }
                }
            },
            "NS": {
                "trafo": {
                    "buslv": {
                        "Sym": [
                            "m:u1:buslv",
                            "m:I1:buslv",
                            "m:I1P:buslv",
                            "m:I1Q:buslv"
                        ],
                        "ULE": [
                            "n:u:buslv:A",
                            "n:u:buslv:B",
                            "n:u:buslv:C"
                        ],
                        "Unsym": [
                            "n:ul:buslv:A",
                            "n:ul:buslv:B",
                            "n:ul:buslv:C",
                            "m:I:buslv:A",
                            "m:I:buslv:B",
                            "m:I:buslv:C",
                            "m:I1P:buslv",
                            "m:I1Q:buslv"
                        ]
                    }
                },
                "line": {
                    "bus2": {
                        "Sym": [
                            "m:u1:bus2",
                            "m:I1:bus2",
                            "m:I1P:bus2",
                            "m:I1Q:bus2"
                        ],
                        "ULE": [
                            "n:u:bus2:A",
                            "n:u:bus2:B",
                            "n:u:bus2:C"
                        ],
                        "Unsym": [
                            "n:ul:bus2:A",
                            "n:ul:bus2:B",
                            "n:ul:bus2:C",
                            "m:I:bus2:A",
                            "m:I:bus2:B",
                            "m:I:bus2:C",
                            "m:I1P:bus2",
                            "m:I1Q:bus2"
                        ]
                    },
                    "bus1": {
                        "Sym": [
                            "m:u1:bus1",
                            "m:I1:bus1",
                            "m:I1P:bus1",
                            "m:I1Q:bus1"
                        ],
                        "ULE": [
                            "n:u:bus1:A",
                            "n:u:bus1:B",
                            "n:u:bus1:C"
                        ],
                        "Unsym": [
                            "n:ul:bus1:A",
                            "n:ul:bus1:B",
                            "n:ul:bus1:C",
                            "m:I:bus1:A",
                            "m:I:bus1:B",
                            "m:I:bus1:C",
                            "m:I1P:bus1",
                            "m:I1Q:bus1"
                        ]
                    }
                }
            },
            "VKM": {
                "ElmSym": {
                    "Sym": [
                        "c:fi",
                        "c:fipol",
                        "c:firel",
                        "c:firot"
                    ],
                    "Unsym": [
                        "c:fi",
                        "c:fipol",
                        "c:firel",
                        "c:firot"
                    ]
                }
            },
            "NAP": {
                "line": {
                    "bus1": {
                        "Sym": [
                            "m:u1:bus1",
                            "m:I1:bus1",
                            "m:I1P:bus1",
                            "m:I1Q:bus1"
                        ],
                        "Unsym": [
                            "n:ul:bus1:A",
                            "n:ul:bus1:B",
                            "n:ul:bus1:C",
                            "m:I:bus1:A",
                            "m:I:bus1:B",
                            "m:I:bus1:C",
                            "m:I1P:bus1",
                            "m:I1Q:bus1"
                        ]
                    }
                }
            }
        }


with open("../data/json_res_vars.txt", "w") as f:
    json.dump(res_vars, f, indent=4)
