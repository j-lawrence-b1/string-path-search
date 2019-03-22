<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@include file="/WEB-INF/view/commons/taglib.jsp"%>
<form class="layui-form layui-box" id="inputForm" style='padding:10px 30px 10px 20px' action="${ctx}/system/productgroup/api/pgroup-clone" data-auto="true" method="post">
    <table class="layui-table">
		<tbody>
			<tr>
				<td><b>源组</b></td>
				<td colspan="2">
					<c:choose>
						<c:when test="${!empty pgroupList}">
							<select name="clonePGroupId">
								<c:forEach var="item" items="${pgroupList}" varStatus="s">
									<option value="${item.id}">${item.productGroupName}</option>
								</c:forEach>
							</select>
						</c:when>
						<c:otherwise>
							<select name="clonePGroupId">
								<option value="0">无克隆产品组</option>
							</select>
						</c:otherwise>
					</c:choose>
				</td>
			</tr>
			<tr>
				<td rowspan="4"><b>目标组</b></td>
				<td>
					<b>运营商</b>
				</td>
				<td>
					<select name="operatorCode" id="operatorCode">
					  	<option value="1">移动</option>
					  	<option value="2">联通</option>
					  	<option value="3">电信</option>
				     </select>
				</td>
			</tr>
			<tr>
				<td>
					<b>省份</b>
				</td>
				<td>
					<select name="provinceCode" id="provinceCode" lay-verify="" lay-search>
		   			</select>
				</td>
			</tr>
			<tr>
				<td>
					<b>产品类型</b>
				</td>
				<td>
		        	<input type="radio" checked name="productType" value="1" title="全国包可漫游">
		        	<input type="radio" name="productType" value="2" title="省包不可漫游">
				</td>
			</tr>
			<tr>
				<td>
					<font color="red">*</font><b>产品组名称</b>
				</td>
				<td>
					<input type="text" name="productGroupName" id="productGroupName" value='全国移动全国包可漫游' readonly class="layui-input">
				</td>
			</tr>
		</tbody>
	</table>
    <div class="layui-form-item text-c">
    	<br><br><br><br>
        <button class="layui-btn" type='submit'>保存数据</button>
        <button class="layui-btn layui-btn-danger" type='button' data-close>取消</button>
    </div>
</form>
<script  type="text/javascript">
    /**
     *自动生成组名称
     */
    function autoGroupName() {
        var ispName = $("#operatorCode>option:selected", $("#inputForm")).text();
        var provinceName = $("#provinceCode>option:selected", $("#inputForm")).text();
        var productType = $("input[name='productType']:checked", $("#inputForm")).val() == "1" ? "全国包可漫游" : "省包不可漫游";
        var productGroupName = provinceName + ispName + productType;
        $("#productGroupName", $("#inputForm")).val(productGroupName);
    }
    
    layui.use(['adminplugs', 'form'], function(){
    	var form = layui.form; 
    	$.myutil.loadProvince();
    	
    	form.on('select', function(){
    		autoGroupName();
   		});
    	
    	form.on('radio', function(data){
    		autoGroupName();
   		}); 
    });
</script>
