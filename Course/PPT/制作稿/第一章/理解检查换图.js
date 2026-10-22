var ch1KnowledgeArtAssets = [{"image_id": "4310560839565312", "path": "ch1-check-confidence.png", "alt": "自信地回答，旁边仍有待核实的参考材料", "source_dimensions": [1536, 1024], "frame": {"left": 117, "top": 294, "width": 378, "height": 252}, "crop": {"left": 0, "top": 0, "right": 0, "bottom": 0}, "aspect_mismatch_percent": 0.0}, {"image_id": "2401372209152000", "path": "ch1-check-repeated-question.png", "alt": "同一个问题与三份尚未判定的回答", "source_dimensions": [1536, 1024], "frame": {"left": 654, "top": 294, "width": 378, "height": 252}, "crop": {"left": 0, "top": 0, "right": 0, "bottom": 0}, "aspect_mismatch_percent": 0.0}, {"image_id": "2401372209152001", "path": "ch1-check-report-reference.png", "alt": "对照原报告和引用内容进行检查", "source_dimensions": [1536, 1024], "frame": {"left": 1178, "top": 294, "width": 378, "height": 252}, "crop": {"left": 0, "top": 0, "right": 0, "bottom": 0}, "aspect_mismatch_percent": 0.0}];
var applyCh1KnowledgeArt = async (artifactRef, index, assetDirectory) => {
  const fs = await import('node:fs/promises');
  const pathModule = await import('node:path');
  const a = ch1KnowledgeArtAssets[index];
  if (!a) throw new Error('Index must be 0, 1 or 2');
  return await artifactSession.run(async ({ presentation }) => {
    const s = presentation.slides.getById('zvlep1');
    const i = s.images.items.find(x => x.id === a.image_id);
    if (!i) throw new Error('Expected image ID is missing: ' + a.image_id);
    await i.replace({dataUrl:'data:image/png;base64,'+(await fs.readFile(pathModule.join(assetDirectory,a.path))).toString('base64'),alt:a.alt,fit:'contain'});
    i.crop=a.crop;
    i.frame=a.frame;
    if(index===2) s.speakerNotes.setText(s.speakerNotes.text.replace('插图复用已确认的ch1-feedback-scene系列三张独立PNG，均按3:2显示','插图使用新生成的ch1-check-confidence、ch1-check-repeated-question和ch1-check-report-reference三张独立PNG，分别对应待核实材料、同一问题的三份回答、对照报告检查引用，均按3:2显示'));
    return {slide_id:s.id,image_id:i.id,asset_id:i.referenceId,source:a.path,frame:i.frame};
  }, {artifactRef,artifactType:'presentation'});
};
var renderCh1KnowledgeCheck = async (artifactRef, assetDirectory, previewPath) => {
  const fs = await import('node:fs/promises');
  const pathModule = await import('node:path');
  return await artifactSession.run(async ({presentation}) => {
    const s=presentation.slides.getById('zvlep1');
    await presentation.hydrateImageAssets(await Promise.all(ch1KnowledgeArtAssets.map(async a=>({assetId:s.images.items.find(i=>i.id===a.image_id).referenceId,data:new Uint8Array(await fs.readFile(pathModule.join(assetDirectory,a.path))),contentType:'image/png'}))));
    const path=previewPath;
    const b=await s.export({format:'png',scale:1});
    await fs.writeFile(path,new Uint8Array(await b.arrayBuffer()));
    return {slide_id:s.id,path,images:s.images.items.map(i=>({id:i.id,ref:i.referenceId,frame:i.frame,crop:i.crop}))};
  },{artifactRef,artifactType:'presentation'});
};
// 在 Artifact Session 中加载上述函数，先用工具连接原课件取得 artifactRef。
// assetDirectory 为本项目 Course/PPT/assets 的绝对路径，由调用方明确传入。
// 分别调用并检查 applyCh1KnowledgeArt(ref, 0, assetDirectory)，再依次传入1、2。
// 每次保存确认后再继续；最后 renderCh1KnowledgeCheck(ref, assetDirectory, previewPath)。
// 所有标题、题目、选项和空白选择框保持原样。Git提交不表示云端已经换图。
