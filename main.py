import sys
sys.path.append('./Model')
sys.path.append('./Merge')
from BuildModel import Model
from Merge import Merge


# 读两个模型
model1 = Model()
model2 = Model()
model1.Build_Model_From_Project('./Data/2020FallSE/181860039_孔鹏翔_AnyMemo')
model2.Build_Model_From_Project('./Data/2020Fall软件方法学/MG20330042_毛心怡_MG20330037_刘疏观_MG1633116_李达_AnyMemo')
print('model1.state_list:', len(model1.state_list))
print('model2.state_list:', len(model2.state_list))
print('model1.transitions:', len(model1.transitions))
print('model2.transitions:', len(model2.transitions))

# 以APP名称定义一个Merge类，加入这两个模型
AnyMemo = Merge()
AnyMemo.add_model(model1)
AnyMemo.add_model(model2)

# 进行模型合并操作，返回合并好的模型
AnyMemo.merge_models()
res = AnyMemo.get_res_model()
print('res.state_list:', len(res.state_list))
print('res.states:', len(res.states))
print('res.transitions:', len(res.transitions))

# 模型可视化：关系图
g = Graph()
g.generate_graph(res)
print(g.vertices)
g.visualization()