// CTF平台MongoDB初始化脚本

// 切换到ctf_challenges数据库
db = db.getSiblingDB('ctf_challenges');

// 创建ctf_user用户
db.createUser({
  user: 'ctf_user',
  pwd: 'ctf_password',
  roles: [
    {
      role: 'readWrite',
      db: 'ctf_challenges'
    }
  ]
});

// 创建题目详情集合
db.createCollection('challenge_details', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['challenge_id', 'content_type'],
      properties: {
        challenge_id: {
          bsonType: 'int',
          description: '题目ID，必须是整数'
        },
        content_type: {
          bsonType: 'string',
          enum: ['writeup', 'source_code', 'docker_config', 'files'],
          description: '内容类型'
        },
        content: {
          bsonType: 'object',
          description: '具体内容'
        },
        metadata: {
          bsonType: 'object',
          description: '元数据信息'
        },
        created_at: {
          bsonType: 'date',
          description: '创建时间'
        },
        updated_at: {
          bsonType: 'date',
          description: '更新时间'
        }
      }
    }
  }
});

// 创建AI生成内容集合
db.createCollection('ai_generated_content', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['generation_id', 'model_name', 'task_type'],
      properties: {
        generation_id: {
          bsonType: 'string',
          description: '生成记录ID'
        },
        model_name: {
          bsonType: 'string',
          description: 'AI模型名称'
        },
        task_type: {
          bsonType: 'string',
          enum: ['challenge', 'flag', 'text', 'writeup'],
          description: '任务类型'
        },
        input_prompt: {
          bsonType: 'string',
          description: '输入提示词'
        },
        generated_content: {
          bsonType: 'object',
          description: '生成的内容'
        },
        quality_score: {
          bsonType: 'number',
          minimum: 0,
          maximum: 1,
          description: '内容质量评分'
        },
        user_feedback: {
          bsonType: 'object',
          description: '用户反馈'
        },
        created_at: {
          bsonType: 'date',
          description: '创建时间'
        }
      }
    }
  }
});

// 创建文件存储集合
db.createCollection('file_storage', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['file_id', 'filename', 'content_type'],
      properties: {
        file_id: {
          bsonType: 'string',
          description: '文件唯一标识'
        },
        filename: {
          bsonType: 'string',
          description: '文件名'
        },
        content_type: {
          bsonType: 'string',
          description: 'MIME类型'
        },
        file_size: {
          bsonType: 'long',
          description: '文件大小（字节）'
        },
        file_hash: {
          bsonType: 'string',
          description: '文件哈希值'
        },
        storage_path: {
          bsonType: 'string',
          description: '存储路径'
        },
        challenge_id: {
          bsonType: 'int',
          description: '关联的题目ID'
        },
        uploaded_by: {
          bsonType: 'int',
          description: '上传用户ID'
        },
        metadata: {
          bsonType: 'object',
          description: '文件元数据'
        },
        created_at: {
          bsonType: 'date',
          description: '创建时间'
        }
      }
    }
  }
});

// 创建用户活动日志集合
db.createCollection('user_activity_logs', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'action', 'timestamp'],
      properties: {
        user_id: {
          bsonType: 'int',
          description: '用户ID'
        },
        action: {
          bsonType: 'string',
          description: '用户行为'
        },
        resource_type: {
          bsonType: 'string',
          description: '资源类型'
        },
        resource_id: {
          bsonType: 'string',
          description: '资源ID'
        },
        details: {
          bsonType: 'object',
          description: '详细信息'
        },
        ip_address: {
          bsonType: 'string',
          description: 'IP地址'
        },
        user_agent: {
          bsonType: 'string',
          description: '用户代理'
        },
        timestamp: {
          bsonType: 'date',
          description: '时间戳'
        }
      }
    }
  }
});

// 创建系统监控数据集合
db.createCollection('system_metrics', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['metric_name', 'value', 'timestamp'],
      properties: {
        metric_name: {
          bsonType: 'string',
          description: '指标名称'
        },
        value: {
          bsonType: 'number',
          description: '指标值'
        },
        tags: {
          bsonType: 'object',
          description: '标签'
        },
        timestamp: {
          bsonType: 'date',
          description: '时间戳'
        }
      }
    }
  }
});

// 创建索引
db.challenge_details.createIndex({ 'challenge_id': 1 });
db.challenge_details.createIndex({ 'content_type': 1 });
db.challenge_details.createIndex({ 'created_at': -1 });

db.ai_generated_content.createIndex({ 'generation_id': 1 }, { unique: true });
db.ai_generated_content.createIndex({ 'model_name': 1 });
db.ai_generated_content.createIndex({ 'task_type': 1 });
db.ai_generated_content.createIndex({ 'created_at': -1 });

db.file_storage.createIndex({ 'file_id': 1 }, { unique: true });
db.file_storage.createIndex({ 'challenge_id': 1 });
db.file_storage.createIndex({ 'uploaded_by': 1 });
db.file_storage.createIndex({ 'file_hash': 1 });

db.user_activity_logs.createIndex({ 'user_id': 1 });
db.user_activity_logs.createIndex({ 'action': 1 });
db.user_activity_logs.createIndex({ 'timestamp': -1 });
db.user_activity_logs.createIndex({ 'resource_type': 1, 'resource_id': 1 });

db.system_metrics.createIndex({ 'metric_name': 1 });
db.system_metrics.createIndex({ 'timestamp': -1 });
db.system_metrics.createIndex({ 'metric_name': 1, 'timestamp': -1 });

// 插入示例数据
db.challenge_details.insertMany([
  {
    challenge_id: 1,
    content_type: 'writeup',
    content: {
      title: '示例题目解题思路',
      steps: [
        '分析题目描述',
        '查看源代码',
        '发现漏洞点',
        '构造payload',
        '获取flag'
      ],
      tools_used: ['Burp Suite', 'Python'],
      difficulty_analysis: '这是一道入门级Web题目，主要考查SQL注入基础知识。'
    },
    metadata: {
      author: 'system',
      language: 'zh-CN',
      version: '1.0'
    },
    created_at: new Date(),
    updated_at: new Date()
  }
]);

db.system_metrics.insertMany([
  {
    metric_name: 'active_users',
    value: 0,
    tags: { type: 'counter' },
    timestamp: new Date()
  },
  {
    metric_name: 'total_challenges',
    value: 0,
    tags: { type: 'gauge' },
    timestamp: new Date()
  },
  {
    metric_name: 'ai_generations_today',
    value: 0,
    tags: { type: 'counter', period: 'daily' },
    timestamp: new Date()
  }
]);

print('MongoDB初始化完成！');
print('数据库: ctf_challenges');
print('用户: ctf_user');
print('集合数量: ' + db.getCollectionNames().length);

