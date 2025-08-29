from fastapi import APIRouter, HTTPException, Request

router = APIRouter()

@router.get("/status")
async def consumer_status(request: Request):
    consumer = request.app.consumer
    return {
        'consumer_status': consumer.get_status() if hasattr(consumer, 'get_status') else 'unknown',
        'queue_status': consumer.get_consumer_status() if hasattr(consumer, 'get_consumer_status') else 'unknown'
    }

@router.get("/test-connection")
async def test_connection(request: Request):
    consumer = request.app.consumer
    try:
        # 注意：这个方法可能需要修改以适应FastAPI
        if hasattr(consumer, '_get_connection'):
            conn = consumer._get_connection()
            try:
                # 测试连接是否有效
                channel = conn.channel()
                channel.close()
                conn.close()
                return {
                    "status": "success",
                    "message": f"成功连接到 {consumer._connection_params.host}:{consumer._connection_params.port}"
                }
            except Exception as e:
                if conn and not conn.is_closed:
                    conn.close()
                raise e
        else:
            # 简单检查连接参数是否存在
            if hasattr(consumer, '_connection_params') and consumer._connection_params:
                return {
                    "status": "info",
                    "message": f"已配置连接参数 {consumer._connection_params.host}:{consumer._connection_params.port}，但未测试实际连接"
                }
            else:
                return {
                    "status": "error", 
                    "message": "未配置连接参数"
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"连接测试失败: {str(e)}")

@router.post("/control/start")
async def start_consumer(request: Request):
    consumer = request.app.consumer
    try:
        if not hasattr(consumer, '_consumer_thread') or consumer._consumer_thread is None:
            consumer.start_consuming()
            return {"status": "success", "message": "消费者已启动"}
        else:
            return {"status": "warning", "message": "消费者已在运行"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动消费者失败: {str(e)}")

@router.post("/control/stop")
async def stop_consumer(request: Request):
    consumer = request.app.consumer
    try:
        if hasattr(consumer, '_consumer_thread') and consumer._consumer_thread is not None:
            consumer.stop_consuming()
            return {"status": "success", "message": "消费者已停止"}
        else:
            return {"status": "warning", "message": "消费者未在运行"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止消费者失败: {str(e)}")