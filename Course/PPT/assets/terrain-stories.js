// Article dialogue beats; time is in seconds at 1×. A/B are independent conversations.
window.terrainStories = {
  "drift-a": {
    "duration": 75.15,
    "route": false,
    "kind": null,
    "events": [
      {
        "at": 0,
        "seconds": 7.07,
        "turn": 0,
        "end": 43,
        "label": "清理一下系统日志",
        "field": [
          1,
          0,
          0,
          0,
          0
        ],
        "position": 0.1
      },
      {
        "at": 7.07,
        "seconds": 5.5,
        "turn": 1,
        "end": 21,
        "label": "确认",
        "field": [
          1,
          0,
          0,
          0,
          0
        ],
        "position": 0.2
      },
      {
        "at": 12.57,
        "seconds": 6.86,
        "turn": 2,
        "end": 40,
        "label": "du -sh",
        "field": [
          1,
          0,
          0,
          0,
          0
        ],
        "position": 0.3
      },
      {
        "at": 19.43,
        "seconds": 8.71,
        "turn": 3,
        "end": 66,
        "label": "40GB",
        "field": [
          1,
          0.15,
          0,
          0,
          0
        ],
        "position": 0.4
      },
      {
        "at": 28.14,
        "seconds": 6.43,
        "turn": 4,
        "end": 34,
        "label": "tail -n 5",
        "field": [
          1,
          0.25,
          0,
          0,
          0
        ],
        "position": 0.48
      },
      {
        "at": 34.57,
        "seconds": 8.29,
        "turn": 5,
        "end": 60,
        "label": "SSL_do_handshake()",
        "field": [
          1,
          0.4,
          0,
          0,
          0
        ],
        "position": 0.58
      },
      {
        "at": 42.86,
        "seconds": 6.5,
        "turn": 6,
        "end": 35,
        "label": "更新 SSL 证书",
        "field": [
          1,
          0.65,
          0,
          0,
          0
        ],
        "position": 0.72
      },
      {
        "at": 49.36,
        "seconds": 9.21,
        "turn": 7,
        "end": 73,
        "label": "DNS challenge failed",
        "field": [
          1,
          0.8,
          0,
          0,
          0
        ],
        "position": 0.83
      },
      {
        "at": 58.57,
        "seconds": 6.79,
        "turn": 8,
        "end": 39,
        "label": "检查 DNS 配置",
        "field": [
          1,
          1,
          0,
          0,
          0
        ],
        "position": 0.94
      },
      {
        "at": 65.36,
        "seconds": 6.79,
        "turn": 9,
        "end": 39,
        "label": "ping 8.8.8.8",
        "field": [
          1,
          1,
          0,
          0,
          0
        ],
        "position": 1
      }
    ]
  },
  "drift-b": {
    "duration": 20.35,
    "route": true,
    "kind": null,
    "events": [
      {
        "at": 0,
        "seconds": 7.21,
        "turn": 0,
        "end": 45,
        "label": "唯一目标是清理磁盘",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 0.35
      },
      {
        "at": 7.21,
        "seconds": 10.14,
        "turn": 1,
        "end": 86,
        "label": "82 GB",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 1
      }
    ]
  },
  "entangle-a": {
    "duration": 22.64,
    "route": false,
    "kind": null,
    "events": [
      {
        "at": 0,
        "seconds": 5.36,
        "turn": 0,
        "end": 19,
        "label": "严谨的架构标准",
        "field": [
          1,
          0.25,
          0,
          0,
          0
        ],
        "position": 0.35
      },
      {
        "at": 5.36,
        "seconds": 6.64,
        "turn": 1,
        "end": 37,
        "label": "DDD",
        "field": [
          1,
          0.6,
          0,
          0,
          0
        ],
        "position": 0.6
      },
      {
        "at": 12.0,
        "seconds": 7.64,
        "turn": 1,
        "end": 88,
        "label": "CQRS",
        "field": [
          1,
          1,
          0,
          0,
          0
        ],
        "position": 1
      }
    ]
  },
  "entangle-b": {
    "duration": 29.79,
    "route": true,
    "kind": null,
    "events": [
      {
        "at": 0,
        "seconds": 6.36,
        "turn": 0,
        "end": 33,
        "label": "字段边界清晰",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 0.35
      },
      {
        "at": 6.36,
        "seconds": 8.57,
        "turn": 1,
        "end": 64,
        "label": "字段定义",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 0.57
      },
      {
        "at": 14.93,
        "seconds": 6.29,
        "turn": 1,
        "end": 96,
        "label": "校验规范",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 0.78
      },
      {
        "at": 21.22,
        "seconds": 5.57,
        "turn": 1,
        "end": 118,
        "label": "直接可运行",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 1
      }
    ]
  },
  "balance-a": {
    "duration": 26.57,
    "route": false,
    "kind": null,
    "events": [
      {
        "at": 0,
        "seconds": 5.64,
        "turn": 0,
        "end": 23,
        "label": "现代科技感",
        "field": [
          1,
          0,
          0,
          0,
          0
        ],
        "position": 0.35
      },
      {
        "at": 5.64,
        "seconds": 12.93,
        "turn": 1,
        "end": 125,
        "label": "安装 Node 环境",
        "field": [
          1,
          1,
          0,
          0,
          0
        ],
        "position": 0.94
      },
      {
        "at": 18.57,
        "seconds": 5,
        "turn": 2,
        "end": 14,
        "label": "什么是 npm",
        "field": [
          1,
          1,
          0,
          0,
          0
        ],
        "position": 1
      }
    ]
  },
  "balance-b": {
    "duration": 22.71,
    "route": true,
    "kind": null,
    "events": [
      {
        "at": 0,
        "seconds": 7.14,
        "turn": 0,
        "end": 44,
        "label": "电脑小白",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 0.35
      },
      {
        "at": 7.14,
        "seconds": 12.57,
        "turn": 1,
        "end": 120,
        "label": "完全不需要任何安装",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 1
      }
    ]
  },
  "purify-a": {
    "duration": 29.21,
    "route": false,
    "kind": null,
    "events": [
      {
        "at": 0,
        "seconds": 13.07,
        "turn": 0,
        "end": 127,
        "label": "未来科技感",
        "field": [
          1,
          0.6,
          0,
          0,
          0
        ],
        "position": 0.35
      },
      {
        "at": 13.07,
        "seconds": 13.14,
        "turn": 1,
        "end": 128,
        "label": "高级人工智能",
        "field": [
          1,
          1,
          0,
          0,
          0
        ],
        "position": 1
      }
    ]
  },
  "purify-b": {
    "duration": 25.43,
    "route": true,
    "kind": null,
    "events": [
      {
        "at": 0,
        "seconds": 7.64,
        "turn": 0,
        "end": 51,
        "label": "贾维斯 J.A.R.V.I.S",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 0.35
      },
      {
        "at": 7.64,
        "seconds": 14.79,
        "turn": 1,
        "end": 151,
        "label": "黑咖啡",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 1
      }
    ]
  },
  "case-better-a": {
    "duration": 20.72,
    "route": false,
    "kind": null,
    "events": [
      {
        "at": 0,
        "seconds": 6.79,
        "turn": 0,
        "end": 39,
        "label": "Linux 环境",
        "field": [
          1,
          0.35,
          0,
          0,
          0
        ],
        "position": 0.35
      },
      {
        "at": 6.79,
        "seconds": 10.93,
        "turn": 1,
        "end": 97,
        "label": "临时文件",
        "field": [
          1,
          1,
          0,
          0,
          0
        ],
        "position": 1
      }
    ]
  },
  "case-better-b": {
    "duration": 20.5,
    "route": true,
    "kind": null,
    "events": [
      {
        "at": 0,
        "seconds": 7.71,
        "turn": 0,
        "end": 52,
        "label": "ls -al | grep",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 0.35
      },
      {
        "at": 7.71,
        "seconds": 9.79,
        "turn": 1,
        "end": 81,
        "label": "管道符",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 1
      }
    ]
  },
  "distill-a": {
    "duration": 39.78,
    "route": true,
    "kind": "purify",
    "events": [
      {
        "at": 0,
        "seconds": 9.07,
        "turn": 0,
        "end": 71,
        "label": "开发者工具",
        "field": [
          1,
          0,
          0,
          0,
          0
        ],
        "position": 0.2
      },
      {
        "at": 9.07,
        "seconds": 10.14,
        "turn": 1,
        "end": 86,
        "label": "Cyberpunk",
        "field": [
          1,
          0.55,
          0,
          0,
          0
        ],
        "position": 0.35
      },
      {
        "at": 19.21,
        "seconds": 8.93,
        "turn": 2,
        "end": 69,
        "label": "极其极简",
        "field": [
          1,
          0.25,
          0.6,
          0.6,
          0.6
        ],
        "position": 0.62
      },
      {
        "at": 28.14,
        "seconds": 8.64,
        "turn": 3,
        "end": 65,
        "label": "Linear 设计美学",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 1
      }
    ]
  },
  "distill-b": {
    "duration": 26.93,
    "route": true,
    "kind": "purify",
    "events": [
      {
        "at": 0,
        "seconds": 8.86,
        "turn": 0,
        "end": 68,
        "label": "Bento Box UI",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 0.35
      },
      {
        "at": 8.86,
        "seconds": 15.07,
        "turn": 1,
        "end": 155,
        "label": "grid-cols-12",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 1
      }
    ]
  },
  "reason-a": {
    "duration": 24.15,
    "route": false,
    "kind": null,
    "events": [
      {
        "at": 0,
        "seconds": 5.86,
        "turn": 0,
        "end": 26,
        "label": "三打白骨精",
        "field": [
          1,
          0,
          0,
          0,
          0
        ],
        "position": 0.35
      },
      {
        "at": 5.86,
        "seconds": 6.93,
        "turn": 1,
        "end": 41,
        "label": "深刻批判",
        "field": [
          1,
          0.7,
          0,
          0,
          0
        ],
        "position": 0.65
      },
      {
        "at": 12.79,
        "seconds": 8.36,
        "turn": 2,
        "end": 61,
        "label": "林黛玉",
        "field": [
          1,
          1,
          0,
          0,
          0
        ],
        "position": 1
      }
    ]
  },
  "reason-b": {
    "duration": 42.0,
    "route": true,
    "kind": null,
    "events": [
      {
        "at": 0,
        "seconds": 5.86,
        "turn": 0,
        "end": 26,
        "label": "三打白骨精",
        "field": [
          1,
          0,
          0,
          0,
          0
        ],
        "position": 0.35
      },
      {
        "at": 5.86,
        "seconds": 8.0,
        "turn": 1,
        "end": 56,
        "label": "鲁迅",
        "field": [
          1,
          0,
          1,
          0,
          0
        ],
        "position": 0.48
      },
      {
        "at": 13.86,
        "seconds": 6.21,
        "turn": 1,
        "end": 87,
        "label": "曹雪芹",
        "field": [
          1,
          0,
          1,
          1,
          0
        ],
        "position": 0.66
      },
      {
        "at": 20.07,
        "seconds": 10.07,
        "turn": 1,
        "end": 172,
        "label": "吴承恩",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 0.84
      },
      {
        "at": 30.14,
        "seconds": 8.86,
        "turn": 1,
        "end": 240,
        "label": "常识性错误",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 1
      }
    ]
  },
  "anneal-a": {
    "duration": 21.93,
    "route": false,
    "kind": null,
    "events": [
      {
        "at": 0,
        "seconds": 6.5,
        "turn": 0,
        "end": 35,
        "label": "具体的行动步骤",
        "field": [
          1,
          0,
          0,
          0,
          0
        ],
        "position": 0.35
      },
      {
        "at": 6.5,
        "seconds": 12.43,
        "turn": 1,
        "end": 118,
        "label": "能加个微信吗",
        "field": [
          1,
          1,
          0,
          0,
          0
        ],
        "position": 1
      }
    ]
  },
  "anneal-b": {
    "duration": 77.65,
    "route": true,
    "kind": null,
    "events": [
      {
        "at": 0,
        "seconds": 11.21,
        "turn": 0,
        "end": 101,
        "label": "先不要",
        "field": [
          1,
          0,
          0.25,
          0,
          0
        ],
        "position": 0.12
      },
      {
        "at": 11.21,
        "seconds": 26.29,
        "turn": 1,
        "end": 312,
        "label": "5 种",
        "field": [
          1,
          0,
          1,
          0,
          0
        ],
        "position": 0.35
      },
      {
        "at": 37.5,
        "seconds": 9.29,
        "turn": 2,
        "end": 74,
        "label": "茶水间",
        "field": [
          1,
          0,
          1,
          1,
          0
        ],
        "position": 0.62
      },
      {
        "at": 46.79,
        "seconds": 8.79,
        "turn": 3,
        "end": 67,
        "label": "求助式破冰",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 0.8
      },
      {
        "at": 55.58,
        "seconds": 19.07,
        "turn": 3,
        "end": 278,
        "label": "谢了",
        "field": [
          1,
          0,
          1,
          1,
          1
        ],
        "position": 1
      }
    ]
  }
};
